# UmaSupporter.FriendServer

이 프로젝트는 [우마서포터] *인자 검색 기능*의 백엔드 서버입니다.

 [우마서포터]: https://github.com/UmaSupporter

## 개발환경

데이터베이스는 MySQL 데이터베이스를 사용하여 개발하였고 [encode/databases] 저장소에서 제공하는 데이터베이스들도 지원할 수 있을거라 기대합니다.  

의존성 관리자로는 [Poetry]를 사용하였습니다. [Poetry Installation 문서](https://python-poetry.org/docs/#installation)의 명령어들로 설치할 수 있습니다. `poetry install` 명령어로 의존성들을 설치하고 `poerty shell` 로 virtualenv가 활성화된 쉘을 사용할 수 있습니다.

[black]을 사용하여 코드 스타일을 관리하고, [mypy]를 이용하여 정적 타입 검사를 합니다.

```
black .
mypy .
```

 [Poetry]: https://python-poetry.org/
 [encode/databases]: https://github.com/encode/databases
 [black]: https://github.com/psf/black/
 [mypy]: https://github.com/python/mypy

## (WIP) Docker

```
docker build .
docker run --name umasupporter -itd -v "$(pwd)/.env":/app/.env -p 8000:8000 <IMAGE_TAG>
```
