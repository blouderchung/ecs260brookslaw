import csv
from datetime import datetime

from pydriller import Repository


def get_intervals(repo_list):
    for repo in repo_list:
        print("Mining repo: ", repo, "...")
        # Init variables for calculate project commit intervals
        is_first_commit = True
        intervals = []
        last_commit_date = datetime(1970, 1, 1, 0, 0, 0, 0)

        author_interval_dict = {}
        try:
            r = Repository(repo).traverse_commits()
        except Exception as error:
            print("[Pydriller] " + repo + " skipped due to unexpected error.", error)
            continue
        try:
            for commit in r:
                try:
                    # Get current commit date
                    date = commit.committer_date
                    if is_first_commit:
                        last_commit_date = date
                        is_first_commit = False
                    intervals.append((date - last_commit_date).total_seconds())
                    last_commit_date = date

                    # Remove alias of author name
                    author_email = commit.author.email
                    author_name = commit.author.name
                    email_segments = author_email.split('@')
                    name2 = author_email
                    if len(email_segments) > 0:
                        name2 = email_segments[0].replace('.', '').lower()
                    name1 = author_name.replace(' ', '').lower()

                    # Calculate each author's max commit intervals in a project
                    if name1 in author_interval_dict.keys():
                        last_date = author_interval_dict[name1][0]
                        curr_interval = (date-last_date).total_seconds()
                        max_interval = author_interval_dict[name1][1]
                        if curr_interval > max_interval:
                            author_interval_dict[name1][1] = curr_interval
                        author_interval_dict[name1][0] = date
                    elif name2 in author_interval_dict.keys():
                        last_date = author_interval_dict[name2][0]
                        curr_interval = (date-last_date).total_seconds()
                        max_interval = author_interval_dict[name2][1]
                        if curr_interval > max_interval:
                            author_interval_dict[name2][1] = curr_interval
                        author_interval_dict[name2][0] = date
                    else:
                        author_interval_dict.update({name1: [date, 0.00]})
                except Exception as error:
                    print('unhandled exception: ', error)
        except Exception as error:
            print("Repository " + repo + " has been skipped due to unexpected error: ", error)
            continue
        write_author_intervals(author_interval_dict)
        write_commit_intervals(repo, intervals)


def read_repo_list(file_dir):
    repo_list = []
    with open(file_dir, newline='') as csv_file:
        list_reader = csv.reader(csv_file)
        index = 0
        for row in list_reader:
            if index != 0:
                repo_list.append(row[1])
            index += 1
            # repo_list.append(row[1])
    return repo_list


def write_commit_intervals(repo, intervals):
    try:
        print('interval writer start')
        with open(commit_interval_file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for interval in intervals:
                writer.writerow([repo, interval])
        print('summary writer complete')
    except:
        print('Unexpected Error when writing interval ', repo)


def write_author_intervals(intervals):
    try:
        print('author interval writer start')
        with open(author_interval_file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for email in intervals.keys():
                interval = intervals[email][1]
                if interval > 0.00:
                    writer.writerow([str(email), interval])
        print('Repo complete')
    except:
        print(email)


author_interval_file_path = 'test_author_intervals.csv'
commit_interval_file_path = 'test_commit_intervals.csv'
if __name__ == '__main__':
    print('Reading csv...')
    repo_list = read_repo_list('test.csv')
    print('Start to get interval list...')
    with open(author_interval_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Name', 'Interval'])
    with open(commit_interval_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Repository', 'Interval'])
    get_intervals(repo_list)
