import time, os

def copy_lines(from_file, to_file):
    try:
        if os.path.exists(to_file):
            os.remove(to_file)
            
        with open(from_file, 'r') as f1, open(to_file, 'w') as f2:
            for line in f1:
                f2.write(line)
                print("line copied")
                time.sleep(0.5)  # Пауза на 10 секунд
    except Exception as e:
        print("Помилка: ", e)
    finally:
        print("done")

from_file = 'from.csv'
to_file = 'test.csv'

copy_lines(from_file, to_file)