import chardet


class LogicException(Exception):
    pass

def allowed_file(filename, config):
    if '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config['ALLOWED_EXTENSIONS']:
        return True
    else:
        raise LogicException(f'File "{filename}" extensions is not allowed.')

def determining_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))
    print(f"Кодировка файла: {result['encoding']} (уверенность: {result['confidence']:.2%})")
    return result