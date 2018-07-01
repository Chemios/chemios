'''
/*
 *
 * Useful Utilities
 *
 */
 '''


def convert_to_lists(df):
    '''Convert data frame to list of lists'''
    output = []
    for i in range(len(list(df))):
        column = df.iloc[:,i]
        output.append(column.values.tolist())       
    for i in output:
        for j in i:
            try:
                x = output[i][j]                
                output[i][j] = x.item()
            except Exception:
                pass
    return output


def import_module(name):
    '''Import a module from a string'''
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
