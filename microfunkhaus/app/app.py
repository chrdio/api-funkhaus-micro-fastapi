import json
import time
from ipaddress import IPv4Address, AddressValueError
from typing import Optional, Set
from fastapi import (
    FastAPI,
    Response,
    Request,
    HTTPException,
    status,
    Path,
    Header,
    Depends,
)
from aiohttp import ClientResponseError, ClientConnectionError
from fastapi.middleware.cors import CORSMiddleware
from ..API import (
    PerformanceRequest,
    LabelingRequest,
    AmendmentRequest,
    PerformanceResponse,
    HEALTHPOINTS,
)
from ..actions import (
    generate_progression,
    send_labels,
    amend_progression,
    healthcheck_dependencies,
)


def generate_app_with_config(
    tokens: Set[str] = {"testing",},
    remote_healthcheck_on_startup: bool = True
    ):

    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        TITLE = config["title"]

    async def check_token(x_token: str = Header()):
        if x_token not in tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    app = FastAPI(
        title=TITLE,
        docs_url="/",
        dependencies=[Depends(check_token)],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_process_time(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = round((time.time() - start_time) * 10**6)
        print(f"Process time: {process_time}µs")
        return response

    # Dependency
    def get_real_ip(request: Request) -> Optional[IPv4Address]:
        try:
            # TestClient supplies an invalid
            # address 'testclient' in requests
            client_address = request.client
            if client_address:
                return IPv4Address(client_address.host)
            else:
                return None  # pragma: no cover (no way to test for now)
        except AddressValueError:
            return IPv4Address("255.255.255.255")

    if remote_healthcheck_on_startup:
        @app.on_event("startup")
        async def startup_event():  # pragma: no cover
            ok = False
            try:
                ok = await healthcheck_dependencies(HEALTHPOINTS)
            finally:
                # This awkward if statement is here
                # so you don't need to re-raise
                # the exception in case of failure
                if not ok:
                    print("Could not establish connections to all of the microservices.")
                else:
                    print("Connections to all of the microservices are established.")

    generation_description = """You can specify the optional key and mode (graph) parameters,
    or even supply the otherwise verbatim progression with a changed key to transpose it."""

    @app.post(
        "/generate",
        summary="Generates a new progression",
        description=generation_description,
        response_description="A generated progression",
        response_model=PerformanceResponse,
        status_code=status.HTTP_200_OK,
    )
    async def gen_progression(
        performance: PerformanceRequest,
        real_ip=Depends(get_real_ip),
    ):
        performance.sess_id = real_ip
        try:
            responses = await generate_progression(performance)
        except ClientResponseError as e:  # pragma: no cover (no way to test for now)
            raise HTTPException(status_code=e.status, detail=e.message)
        return responses

    amendment_description = """It is crucially important to provide a valid performance object,
    copied verbatim from the response of the '/generate' endpoint."""

    @app.post(
        "/amend/{index}",
        summary="Changes a specified chord in a progression",
        description=amendment_description,
        response_description="An amended progression",
        response_model=PerformanceResponse,
        status_code=status.HTTP_200_OK,
    )
    async def amend_performance(
        full_request: AmendmentRequest,
        index: int = Path(
            ...,
            title="Index",
            description="The chord under this index will be substituted",
            example=1,
        ),
        real_ip=Depends(get_real_ip),
    ):
        full_request.sess_id = real_ip
        try:
            responses = await amend_progression(full_request, index)
        except ClientResponseError as e:  # pragma: no cover (no way to test for now)
            raise HTTPException(status_code=e.status, detail=e.message)
        return responses

    @app.post("/label")
    async def label_progression(
        labeling_request: LabelingRequest,
        real_ip=Depends(get_real_ip),
    ):
        labeling_request.sess_id = real_ip
        try:
            await send_labels(labeling_request)
        except ClientResponseError as e:  # pragma: no cover (no way to test for now)
            raise HTTPException(status_code=e.status, detail=e.message)
        return Response(status_code=201)

    @app.get("/healthcheck")
    async def healthcheck():
        try:
            ok = await healthcheck_dependencies(HEALTHPOINTS)
            return Response(status_code=200)
        except ClientConnectionError as e:  # pragma: no cover (no way to test for now)
            raise HTTPException(status_code=429, detail="Not all remotes are healthy.")

    return app
