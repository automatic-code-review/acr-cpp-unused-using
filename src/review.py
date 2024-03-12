import hashlib
import os


def review(config):
    diffs = config['merge']['changes']
    path_source = config['path_source']
    custom_depara = config['custom']

    comments = []

    for diretorio_raiz, _, arquivos in os.walk(path_source):
        for arquivo in arquivos:
            if arquivo.endswith(('.h', '.cpp')):
                caminho_completo = os.path.join(diretorio_raiz, arquivo)
                caminho_relativo = caminho_completo.replace(path_source, "")[1:]

                if not __is_path_in_diff(caminho_relativo, diffs):
                    continue

                with open(caminho_completo, 'r') as f:
                    linhas = f.readlines()
                    usings = []

                    current_line = 0
                    for linha in linhas:
                        current_line += 1
                        if linha.startswith("using "):
                            parts = linha.split(':')
                            name = parts[len(parts) - 1].replace("\n", "").replace(";", "")
                            usings.append({
                                "name": name,
                                "startInLine": current_line,
                            })

                    for using in usings:
                        using_name = using['name']

                        if not __contains_one(linhas, using_name, custom_depara):
                            comments.append(__create_comment(
                                message=f"Using {using_name} não utilizado no arquivo {caminho_relativo}",
                                path=caminho_relativo,
                                start_in_line=using['startInLine']
                            ))

    return comments


def __contains_one(linhas, using_name, custom_depara):
    strings_to_compare = __get_strings_to_compare(using_name, custom_depara)

    for linha in linhas:
        if linha.startswith("using "):
            continue

        for string_to_compare in strings_to_compare:
            if string_to_compare in linha:
                return True

    return False


def __get_strings_to_compare(using_name, custom_depara):
    strings = [using_name]

    for depara in custom_depara:
        if depara['name'] == using_name:
            strings.extend(depara['usingBy'])

    return strings


def __is_path_in_diff(path, diffs):
    for diff in diffs:
        if path == diff['new_path']:
            return True

    return False


def __create_comment(message, path, start_in_line):
    comment = {
        "id": __generate_md5(f"{message} | {start_in_line} | {path}"),
        "comment": message.replace("${FILE_PATH}", path),
        "position": {
            "path": path,
            'language': 'c++',
            "startInLine": start_in_line,
            "endInLine": start_in_line
        }
    }

    return comment


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()
