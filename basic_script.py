import os, json, shutil, sys
from subprocess import run, PIPE

GAME_DIR_PATTERN = "game"
GAME_CODE_EXT = ".go"
GAME_COMPILE_CMD = ["go", "build"]


def find_all_games(source):
    game_paths = []
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
        break
    return game_paths


def get_name_from_paths(paths, to_strip_part):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip_part, "")
        new_names.append(new_dir_name)
    return new_names


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)


def make_json_metadata_file(path, game_dirs):
    data = {"gameName": game_dirs, "noOfGames": len(game_dirs)}
    with open(path, "w") as file:
        json.dump(data, file)


def compile_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXT):
                code_file_name = file
                break
        break
    if code_file_name is None:
        return
    cmd = GAME_COMPILE_CMD + [code_file_name]
    run_cmd(cmd, path)


def run_cmd(cmd, path):
    cwd = os.getcwd()
    os.chdir(path)
    result = run(cmd, universal_newlines=True, stdout=PIPE, stdin=PIPE)
    print("compile result: ", result)
    os.chdir(cwd)


def main(source, target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)
    game_paths = find_all_games(source_path)
    create_dir(target_path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_code(dest_path)
    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)


if __name__ == "__main__":
    args = sys.argv
    # print(args):
    if len(args) != 3:
        raise Exception("You must pass both source and destination")
    source, target = args[1:]
    main(source, target)
