import pandas as pd
import sys


def get_data():
    
    '''
    Asks user to enter the needed version
    Gets data from directory
    Puts the needed columns in a dataframe format
    Handles errors in case of wrong version input
    '''
    entered_version = sys.argv[1]
    while True:
        try:
            version = str(float(entered_version))
            llt_headres = ['llt_code','llt_name','pt_code','llt_whoart_code','llt_harts_code',
                           'llt_costrart_sym','llt_icd9_code','llt_icd9cm_code','llt_icd10_code',
                           'llt_currency','llt_jart_code','none']
            mdhier_headers = ['pt_code','hlt_code','hlgt_code','soc_code','pt_name','hlt_name',
                              'hlgt_name','soc_name','soc_abbrev','null_field','pt_soc_code',
                              'primary_soc_fg','none']
            llt_raw = pd.read_csv('versions/'+version+'/llt.asc',
                                  delimiter='$', names=llt_headres)
            mdhier_raw = pd.read_csv('versions/'+version+'/mdhier.asc',
                                     delimiter='$', names=mdhier_headers)
            llt = llt_raw[['llt_code','llt_name','pt_code']]
            mdhier = mdhier_raw[['pt_code','pt_name','hlt_code','hlt_name','hlgt_code','hlgt_name',
                                 'soc_code','soc_name']]
            break
        except (ValueError, FileNotFoundError):
            entered_version = input('Invalid Version number! Please make sure you input a valid version number: ')
    return llt , mdhier


llt , mdhier = get_data()


def get_key_words():
    
    '''
    Asks user to enter the desired search string and puts it in lower cases
    Splits the string into words and removes non-keywords
    '''
    
    entered_str = sys.argv[2]
    search_str = entered_str.lower()
    search_words = search_str.split()
    unwanted = ['a','an','the','of','in','into','inside','on','onto','up','upon','under','with',
                'without','and','or','as','at','to','from','due','no','not','non','about','above',
                'over','across','after','along','around','before','below','beside','between','by',
                'during','near','out','outside','via','within','any','for','like','.',',','-','&',
                ')','(',' ',';',':','*','?','"','<','>','|','/','\\']
    for word in search_words:
        if word in unwanted:
            search_words.remove(word)
    return search_words


search_words = get_key_words()


def get_matching_llts():
    
    '''
    Finds the LLTs unique matches
    '''
    
    matched_llts = set()
    for key_word in search_words:
        matched_rows = llt[llt['llt_name'].str.contains(key_word, na=False)]
        matched_llts.update(matched_rows['llt_name'].tolist())
    unique_matches = list(matched_llts)
    return unique_matches


unique_matches = get_matching_llts()


def get_dataframe():
    
    '''
    Performs search operation and put the result in a dataframe format
    '''
    
    result_dict = {}
    dict_key = 1
    for match in unique_matches:
        lltcode = list(llt.loc[llt.llt_name == match]['llt_code'])[0]
        ptcode = list(llt.loc[llt.llt_name == match]['pt_code'])[0]
        matched_pt = mdhier.loc[mdhier.pt_code == ptcode]

        for pt_frequency in range(len(matched_pt)):
            result_dict[dict_key] = [lltcode, match, ptcode,
                                     matched_pt.iloc[pt_frequency]['pt_name'],
                                     matched_pt.iloc[pt_frequency]['hlt_code'],
                                     matched_pt.iloc[pt_frequency]['hlt_name'],
                                     matched_pt.iloc[pt_frequency]['hlgt_code'],
                                     matched_pt.iloc[pt_frequency]['hlgt_name'],
                                     matched_pt.iloc[pt_frequency]['soc_code'],
                                     matched_pt.iloc[pt_frequency]['soc_name']]
            dict_key += 1
    result_schedual = pd.DataFrame(result_dict, index=('LLT Code','LLT','PT Code',
                                                       'PT','HLT Code','HLT','HLGT Code',
                                                       'HLGT','SOC Code','SOC')).T
    return result_schedual


result_schedual = get_dataframe()


def export_csv():
    
    '''
    Exports the result dataframe to a csv file
    Handles errors in case of failed exporting
    '''
    
    try:
        search_str = ''
        for counter in range(len(search_words)):
            search_str += search_words[counter] + ' '
        result_schedual.to_csv('{}search result.csv'.format(search_str))
    except PermissionError:
        print('This exact search was done before and the old file is opened so it can not be replaced. Please close the old file and try again. ')


export_csv()
