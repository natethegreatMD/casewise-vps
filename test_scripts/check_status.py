import asyncio
from casewise.grading.grader import Grader

async def check_status():
    grader = Grader()
    session = await grader.get_session_status('a95cb16e-c3d5-4983-aac7-5624a00bcb63')
    
    if session:
        print(f"Status: {session.status.value}")
        print(f"Error: {session.error_message if session.error_message else 'None'}")
        if session.result:
            print(f"Score: {session.result.total_score}")
    else:
        print("Session not found")

if __name__ == "__main__":
    asyncio.run(check_status()) 