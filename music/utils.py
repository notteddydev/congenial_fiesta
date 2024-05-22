def get_tune_id_from_file_name(file_name):
    file_name_split = file_name.split('-_-')
    str_id = file_name_split[2][:-4]
    return int(str_id)