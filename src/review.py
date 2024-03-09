import hashlib
import os


def review(config):
    diffs = config['merge']['changes']
    path_source = config['path_source']

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
                        found = False
                        using_name = using['name']

                        for linha in linhas:
                            if linha.startswith("using "):
                                continue

                            if using_name in linha:
                                found = True
                                break

                        if not found:
                            comments.append(__create_comment(
                                message=f"Using {using_name} não utilizado no arquivo {caminho_relativo}",
                                path=caminho_relativo,
                                start_in_line=using['startInLine']
                            ))

    return comments


def __is_path_in_diff(path, diffs):
    for diff in diffs:
        if path == diff['new_path']:
            return True

    return False


def __create_comment(message, path, start_in_line):
    comment = {
        "id": __generate_md5(message),
        "comment": message.replace("${FILE_PATH}", path),
        "position": {
            "path": path,
            "snipset": True,
            "startInLine": start_in_line
        }
    }

    return comment


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()
