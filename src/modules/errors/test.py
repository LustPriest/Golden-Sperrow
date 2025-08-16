from src.router import router


@router.command("testerror")
async def test_error_command(_, __):
    msg = "Test Error Message"
    raise Exception(msg)
