from mlsearch.config import Config
from mlsearch.protocol import Protocol
from github import Github
from requests.auth import HTTPBasicAuth
import googleapiclient.discovery
import json
import requests
import html

# import scholarly


class APIRequest:
    """For handling the different Valid API requests."""

    def __init__(self, source, query, init_idx, count, y_next_page_token=None):
        """
        Initialization for the class.

        :param  source:     The API request destination.
        :param  query:      The query for searching.
        :param  init_idx:   The initial pagination index.
        :param  count:      The number of records to be fetched.
        :param  y_next_page_token: The current page token for youtube API.
        """

        self.params = {
            "query": query,
            "init_idx": init_idx,
            "count": count,
            "source": source,
            "y_next_page_token": y_next_page_token,
        }
        self.params_model = {"query": str, "init_idx": int, "count": int}
        # Load the configuration file
        self._config = Config
        # Validate Params
        self._validate_params()
        # Response data
        self.data = {
            "response_code": 201,
            "content": None,
            "has_next_page": False,
            "y_next_page_token": None,
        }

    @property
    def youtube_query_order(self):
        return self._config.YOUTUBE_ORDER

    @youtube_query_order.setter
    def youtube_query_order(self, youtube_order):
        if youtube_order:
            self._config.YOUTUBE_ORDER = youtube_order

    @property
    def github_acc_token(self):
        return self._config.GITHUB_ACC_TOKEN

    @github_acc_token.setter
    def github_acc_token(self, access_token):
        if access_token:
            self._config.GITHUB_ACC_TOKEN = access_token

    @property
    def youtube_developer_key(self):
        return self._config.YOUTUBE_DEVELOPER_KEY

    @youtube_developer_key.setter
    def youtube_developer_key(self, developer_key):
        if developer_key:
            self._config.YOUTUBE_DEVELOPER_KEY = developer_key

    @property
    def pwc_auth_info(self):
        return (self._config.PWC_USER_NAME, self._config.PWC_PASSWORD)

    @pwc_auth_info.setter
    def pwc_auth_info(self, auth_info: "tuple(user_name, password)"):
        assert isinstance(
            auth_info, tuple
        ), f"Invalid type for auth_info. Expected tuple but got {type(auth_info)}."
        if len(auth_info) == 2:
            assert isinstance(
                auth_info[0], str
            ), f"Invalid type for user_name. Expected str but got {type(auth_info[0])}."
            assert isinstance(
                auth_info[1], str
            ), f"Invalid type for password. Expected str but got {type(auth_info[1])}."
            self._config.PWC_USER_NAME = auth_info[0]
            self._config.PWC_PASSWORD = auth_info[1]
        else:
            raise AttributeError(
                f"Expected tuple with length 2 but got {len(auth_info)}."
            )

    def _validate_params(self):
        """Validate user input data."""

        for item, typ in self.params_model.items():
            if item in self.params.keys() and not typ == type(self.params[item]):
                raise TypeError(
                    f"Invalid type for {item}. {typ} is expected but "
                    f"{type(self.params[item])} is given."
                )
        if self.params["source"] not in self._config.VALID_API_SOURCE:
            raise ValueError(
                f"Invalid value for {self.params['source']}. "
                f"Expected values are {self._config.VALID_API_SOURCE}"
            )

    def _is_valid_pagination(self, max_count=0):
        """Validate pagination."""
        # If init_idx is greater than acutal content
        if max_count == 0 or self.params["init_idx"] > max_count:
            return False

        # Update pagination flag.
        self.data["has_next_page"] = (
            self.params["init_idx"] + self.params["count"] < max_count
        )

        return True

    def _unescape(self, text):
        """Unescape Html Script."""
        if text and isinstance(text, str):
            return html.unescape(text)
        return text

    def _fetch_github(self) -> [Protocol]:
        """Fetch Github Repository"""

        github = Github(self._config.GITHUB_ACC_TOKEN)
        query = "+".join([self.params["query"], self._config.GITHUB_URL])
        responses = github.search_repositories(query, "stars", "desc")
        results = []

        if not self._is_valid_pagination(responses.totalCount):
            return

        for response in responses[
            self.params["init_idx"] : min(
                self.params["init_idx"] + self.params["count"], responses.totalCount
            )
        ]:

            data = {
                "repository_url": self._unescape(
                    response.clone_url.replace(".git", "")
                ),
                "title": self._unescape(response.name),
                "description": self._unescape(response.description),
                "private": self._unescape(response.private),
                "fork": self._unescape(response.fork),
                "updated_at": self._unescape(
                    response.updated_at.strftime("%Y%m%dT%H:%M:%S")
                ),
                "stargazers_count": self._unescape(response.stargazers_count),
                "watchers_count": self._unescape(response.watchers_count),
                "language": self._unescape(response.language),
                "forks_count": self._unescape(response.forks_count),
                "source": self.params.get("source", ""),
            }
            results.append(Protocol(data))

        self.data["response_code"] = 200
        self.data["content"] = [proto.to_JSON() for proto in results]

    def _fetch_paperwithcode(self) -> [Protocol]:
        """Fetch Paper with Code Repository"""

        results = []
        url = f"{self._config.PWC_URL}{self.params['query']}"
        query_result = requests.get(
            url,
            auth=HTTPBasicAuth(self._config.PWC_USER_NAME, self._config.PWC_PASSWORD),
        )

        if query_result.status_code == 200:
            content = json.loads(query_result.content)
            max_content = len(content)
            if not self._is_valid_pagination(max_content):
                return

            content = content[
                self.params["init_idx"] : min(
                    self.params["init_idx"] + self.params["count"], max_content
                )
            ]

            for item in content:
                data = {
                    "title": self._unescape(item.get("paper_title", None)),
                    "description": self._unescape(item.get("paper_abstract", None)),
                    "paper_url": self._unescape(item.get("paper_url", None)),
                    "num_of_implementations": self._unescape(
                        item.get("number_of_implementations", None)
                    ),
                    "tasks": self._unescape(item.get("tasks", None)),
                    "paper_conference": self._unescape(
                        item.get("paper_conference", None)
                    ),
                    "repository_url": self._unescape(item.get("repository_url", None)),
                    "repository_name": self._unescape(
                        item.get("repository_name", None)
                    ),
                    "repository_framework": self._unescape(
                        item.get("repository_framework", None)
                    ),
                    "repository_stars": self._unescape(
                        item.get("repository_stars", None)
                    ),
                    "paper_published": self._unescape(
                        item.get("paper_published", None)
                    ),
                    "pwc_url": self._unescape(item.get("pwc_url", "")),
                    "source": self.params.get("source", ""),
                }
                results.append(Protocol(data))

            self.data["content"] = [proto.to_JSON() for proto in results]

        self.data["response_code"] = query_result.status_code

    def _fetch_youtube(self, y_next_page_token=None) -> [Protocol]:
        """Fetch the Youtube Repository"""
        results = []
        input_query = str(self.params["query"]).lower().strip()
        user_query = input_query

        if not self._config.YOUTUBE_FIX_KEYWORD.strip() in user_query:
            user_query = input_query + self._config.YOUTUBE_QUERY_FILTER

        youtube = googleapiclient.discovery.build(
            self._config.YOUTUBE_SERVICE_NAME,
            self._config.YOUTUBE_API_VERSION,
            developerKey=self._config.YOUTUBE_DEVELOPER_KEY,
        )
        request = youtube.search().list(
            part=self._config.YOUTUBE_PART,
            maxResults=self.params["count"],
            order=self._config.YOUTUBE_ORDER,
            q=user_query,
            safeSearch=self._config.YOUTUBE_SAFESEARCH,
            pageToken=y_next_page_token,
        )
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            for item in response["items"]:
                # Skip if the video id is null
                if not item.get("id", dict({"videoId": None})).get("videoId", None):
                    continue

                data = {
                    "video_id": self._unescape(
                        item.get("id", dict({"videoId": None})).get("videoId", None)
                    ),
                    "title": self._unescape(
                        item.get("snippet", dict({"title": None})).get("title", None)
                    ),
                    "description": self._unescape(
                        item.get("snippet", dict({"description": None})).get(
                            "description", None
                        )
                    ),
                    "channel_id": self._unescape(
                        item.get("snippet", dict({"channelId": None})).get(
                            "channelId", None
                        )
                    ),
                    "channel_title": self._unescape(
                        item.get("snippet", dict({"channelTitle": None})).get(
                            "channelTitle", None
                        )
                    ),
                    "live_broadcast_content": self._unescape(
                        item.get("snippet", dict({"liveBroadcastContent": None})).get(
                            "liveBroadcastContent", None
                        )
                    ),
                    "published_datetime": self._unescape(
                        item.get("snippet", dict({"publishedAt": None})).get(
                            "publishedAt", None
                        )
                    ),
                    "thumbnails": self._unescape(
                        item.get("snippet", dict({"thumbnails": None})).get(
                            "thumbnails", None
                        )
                    ),
                    "source": self.params.get("source", ""),
                }
                results.append(Protocol(data))
            self.data["y_next_page_token"] = response.get("nextPageToken", None)
            self.data["content"] = [proto.to_JSON() for proto in results]
            self.data["has_next_page"] = (
                response.get("pageInfo", dict({"totalResults": 0})).get(
                    "totalResults", 0
                )
                > 0
            )
            self.data["y_query_order"] = self._config.YOUTUBE_ORDER
        self.data["response_code"] = 200

    def fetch_data(self) -> json:
        """Fetch the data from designated API source."""

        try:
            if self.params.get("source", "") == "paperwithcode":
                self._fetch_paperwithcode()

            if self.params.get("source", "") == "github":
                self._fetch_github()

            if self.params.get("source", "") == "youtube":
                if not self._config.YOUTUBE_ORDER in self._config.VALID_YOUTUBE_ORDER:
                    self.data["response_code"] = 400
                    self.data["content"] = "Invalid Youtube Query Order."
                    return self.data

                self._fetch_youtube(self.params.get("y_next_page_token", None))

            # TODO: Implement the function for Coursera. However, this function
            # may be handled by the backend server.
            if self.params.get("source", "") == "coursera":
                pass

        except Exception as ex:
            self.data["response_code"] = 500
            self.data["content"] = str(ex)

        return self.data
