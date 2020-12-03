from collections import defaultdict, OrderedDict
from olutils import countiter, display
from warnings import warn

EMPTY_VAL = None


def compute_colstats(data, fill_thld=0.1, empty_val=EMPTY_VAL, as_list=False,
                      verbose=False):
    """Compute statistics for each column of dataframe

    Args:
        data (pandas.DataFrame)
        fill_thld (float)           : min filling ratio for sufficient quality
        empty_val (scalar-object)   : dft value when no number can be computed
        as_list (bool)              : get result as list
        verbose (int)               : level of verbose
            0 for None
            n>0, some display (update iteration counter every n iteration)

    Return:
        if as_list:
            (list[OrderedDict])
        else:
            (dict): stats of each column in OrderedDict
        where stats for given as OrderedDict:
            {
                'empty_row_nb': (int),
                'total_usage': (int),
                'filling_ratio': (float),
                'uniq_val_nb': (int),
                'uniq_val_95prc_usage_nb': (float),
                '95prc_usage_val_nb': (int),
                'sufficient_quality': (0 or 1),
                'comment': (str),
                'max_occurrences_value': (scalar-object),
                'max_occurrences_count': (int),
                'min_occurrences_value': (scalar-object),
                'min_occurrences_count': (int),
                'max_value': (scalar-object),
                'min_value': (scalar-object),
            }
    """
    vbatch = None if not verbose else verbose
    display(". compute root column stats", v=verbose)
    stats_by_col = root_colstats(data, empty_val=empty_val, vbatch=vbatch)
    row_n = len(data)
    display(". enrich column stats", v=verbose)
    stats_by_col = enrich_colstats(
        stats_by_col, row_n, fill_thld=fill_thld, verbose=verbose
    )

    if not as_list:
        return stats_by_col

    display(". convert stats dictionary to list", v=verbose)
    rows = []
    for i, (col, colstats) in enumerate(stats_by_col.items(), 1):
        row = OrderedDict([('order', i), ('column', col)])
        for indicator, value in colstats.items():
            row[indicator] = value
        rows.append(row)
    return rows


def root_colstats(data, empty_val=EMPTY_VAL, vbatch=1):
    """Build root statistics for column in data

    Args:
        data (pandas.DataFrame)
        empty_val (scalar-object): default value when no number can be computed
        vbatch (int): number of iteration on columns b/w each display

    Return:
        (dict): stats of each column in OrderedDict
    """
    row_n = len(data)
    stats_by_col = OrderedDict()
    for column in countiter(data.columns.values, vbatch=vbatch):
        series = data[column]

        values_nb = series.count()
        occurrences = list(series.value_counts().iteritems())
        values = len(occurrences)

        stats_by_col[column] = OrderedDict([
            ('empty', row_n - values_nb),
            ('occurrences', occurrences),
            ('filling_ratio', values_nb / row_n),
            ('values', values),
            ('val_occ_max', occurrences[0] if occurrences else (empty_val, 0)),
            ('val_occ_min', occurrences[-1] if occurrences else (empty_val, 0)),
        ])
    return stats_by_col


def enrich_colstats(stats_by_col, row_n, fill_thld=0.1, verbose=None):
    """Enrich stats created by root_colstats

    Args:
        stats_by_col (dict): stat per column
        row_n (int): number of rows in original data (for ratio computation)
        fill_thld (float): min tolerated filling ratio for sufficient quality

    Return:
        (dict): enriched stats of each column in OrderedDict
    """
    ind_by_col = OrderedDict()
    counter = defaultdict(int)
    for col, colstats in stats_by_col.items():

        # Usage
        total_usage = row_n - colstats['empty']
        values = [val for val, _ in colstats['occurrences']]

        # Group of values with same number of uses
        val_grps = []  # List of [nb of vals, nb of usage per vals]
        for _, val_usage in colstats['occurrences']:
            if not val_grps:
                val_grps.append([1, val_usage])
                continue
            lst_grp = val_grps[-1]
            if val_usage == lst_grp[1]:
                lst_grp[0] += 1
            else:
                val_grps.append([1, val_usage])

        # val_95prc_usage is the number of values required to reach 95% usage,
        # # when values of similar used they are all counted at once
        val_95prc_usage = 0
        usage = 0
        for val_nb, val_usage in val_grps:
            if usage >= (0.95 * total_usage):
                break
            usage += val_nb * val_usage
            val_95prc_usage += val_nb

        # Quality
        reason = EMPTY_VAL
        if colstats['filling_ratio'] < fill_thld:
            reason = f"filling_ratio < {fill_thld}"
        elif colstats['values'] == 1:
            reason = "only one value"
        is_sufficient = int(reason is None)
        counter['insufficient'] += (1 - is_sufficient)

        # Compute max, min
        try:
            max_value = max(values) if values else EMPTY_VAL
            min_value = min(values) if values else EMPTY_VAL
        except TypeError as err:
            warn(f"TypeError when building min, max value of column '{col}': {err}")
            min_value, max_value = None, None


        # Filling stats
        ind_by_col[col] = OrderedDict([
            # Filling
            ('empty_row_nb', colstats['empty']),
            ('total_usage', total_usage),
            ('filling_ratio', colstats['filling_ratio']),

            # Usage
            ('uniq_val_nb', colstats['values']),
            #         ('uniq_val_95prc_usage_nb', uniq_val_95prc_usage),
            ('95prc_usage_val_nb', val_95prc_usage),
            ('sufficient_quality', is_sufficient),
            ('comment', reason),
            ('max_occurrences_value', colstats['val_occ_max'][0]),
            ('max_occurrences_count', colstats['val_occ_max'][1]),
            ('min_occurrences_value', colstats['val_occ_min'][0]),
            ('min_occurrences_count', colstats['val_occ_min'][1]),
            ('max_value', max_value),
            ('min_value', min_value),
        ])

    if verbose:
        col_nb = len(ind_by_col)
        count = counter['insufficient']
        prc = 100 * count / col_nb
        print(f"{prc:0.2f}% ({count}/{col_nb}) columns have not enough data")

    return ind_by_col
