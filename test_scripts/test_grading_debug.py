import asyncio
import json
from casewise.grading.grader import Grader
from casewise.models.grading import GradingRequest
from casewise.rubrics.loader import RubricLoader
from casewise.utils.case_loader import CaseLoader

async def test_grading_debug():
    """Test grading process step by step to identify issues."""
    
    print("=== Testing Grading Process Step by Step ===\n")
    
    try:
        # 1. Test rubric loading
        print("1. Testing rubric loading...")
        rubric_loader = RubricLoader()
        rubric = await rubric_loader.load_rubric("tcga_ovarian_cancer")
        print(f"   ✓ Rubric loaded: {rubric.metadata.title}")
        
        # 2. Test case loading
        print("2. Testing case loading...")
        case_loader = CaseLoader()
        case = await case_loader.load_case("case-001")
        print(f"   ✓ Case loaded: {case.metadata.title}")
        
        # 3. Test GPT client initialization
        print("3. Testing GPT client...")
        from casewise.ai.gpt_client import GPTClient
        gpt_client = GPTClient()
        print(f"   ✓ GPT client initialized with model: {gpt_client.model}")
        
        # 4. Test prompt building
        print("4. Testing prompt building...")
        from casewise.ai.prompt_templates import PromptTemplates
        prompt_builder = PromptTemplates()
        prompt = prompt_builder.build_grading_prompt(
            rubric.dict(), 
            "Test student response", 
            case.content
        )
        print(f"   ✓ Prompt built (length: {len(prompt)} chars)")
        
        # 5. Test GPT response generation
        print("5. Testing GPT response generation...")
        system_message = prompt_builder.get_grading_system_message()
        
        # Use a simple test prompt first
        test_prompt = "Please respond with a simple JSON object: {\"test\": \"success\"}"
        
        try:
            result = await gpt_client.generate_response(
                prompt=test_prompt,
                system_message="You are a helpful assistant that responds in JSON format.",
                max_tokens=100,
                temperature=0.1
            )
            print(f"   ✓ GPT response successful: {result['content']}")
        except Exception as e:
            print(f"   ✗ GPT response failed: {str(e)}")
            return
        
        # 6. Test full grading process
        print("6. Testing full grading process...")
        grader = Grader()
        
        # Create a test request
        request = GradingRequest(
            rubric_id="tcga_ovarian_cancer",
            case_id="case-001",
            user_id="test-user",
            student_response="There is a complex bilateral adnexal mass with mixed solid and cystic components. Trace ascites is present. Multiple soft tissue peritoneal implants are noted along the paracolic gutters and in the left upper quadrant adjacent to the spleen. These findings are suggestive of primary ovarian carcinoma with peritoneal spread.",
            additional_context="Student is a radiology resident in their third year."
        )
        
        # Submit grading
        response = await grader.grade_submission(request)
        print(f"   ✓ Grading submitted: {response.session_id}")
        
        # Wait a bit and check status
        await asyncio.sleep(2)
        
        session = await grader.get_session_status(response.session_id)
        if session:
            print(f"   Session status: {session.status.value}")
            if session.error_message:
                print(f"   Error message: {session.error_message}")
        else:
            print("   ✗ Session not found")
            
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_grading_debug()) 