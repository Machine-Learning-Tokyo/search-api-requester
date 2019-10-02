from github import Github


def get_response(github, keywords):
    query = '+'.join(keywords) + '+in:readme+in:description'
    result = github.search_repositories(query, 'stars', 'desc')

    print(f'Found {result.totalCount} repo(s)')

    count = 100

    github_result = {}

    for repo in result:
        url = repo.clone_url.replace('.git', '')
        labels = repo.get_labels()
        stars = repo.stargazers_count
        github_result[url] = stars
        count -= 1
        if count <= 0:
            return github_result


def github_requester(access_token, keywords):
    github = Github(access_token)
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    return get_response(github, keywords)


