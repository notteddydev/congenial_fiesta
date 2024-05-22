import os

def get_tune_id_from_file_name(file_name):
    file_name_split = file_name.split('-_-')
    str_id = file_name_split[2][:-4]
    return int(str_id)

def get_existing_tune_file_name_by_tune_id(tune_id):
    tune_file_names = os.listdir(os.environ.get('TUNES_DIR'))

    tune_gen = (
        tune_file_name for tune_file_name in tune_file_names
        if tune_id == get_tune_id_from_file_name(tune_file_name)
    )
    
    return next(tune_gen, None)