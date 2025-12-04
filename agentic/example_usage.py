"""
Example usage of the KnowledgeBaseService class.
This demonstrates how to use the service class directly (outside of Azure Functions).
"""
import logging
import os
from dotenv import load_dotenv
from knowledgebase_service import KnowledgeBaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

def main():
    """Example usage of KnowledgeBaseService."""
    service = KnowledgeBaseService()
    
    assistant_message = "The name of the phases are usually the file names, only return those names. Finally append a list of phases to be added."
    user_message = """Give me your analysis and best suited phases to create the recipe with the following requirements: 
    Asks operators if they have read the instructions before starting the operation, choices should be given to the operators. 
    After confirming that, the starting time should be noted and the operator starts testing the vials. 
    After each test the operator also weighs individual vials if the weigh is outside the bounds of the given weight requirement 
    then the operator should note down that vial and continue testing the others. 
    After the testing is complete, the failed vials and the total vials should be shown in a table. 
    At the end the end time should be noted."""
    
    try:
        response = service.retrieve(
            assistant_message=assistant_message,
            user_message=user_message
        )
        
        print("\n" + "="*80)
        print("KNOWLEDGE BASE RESPONSE")
        print("="*80)
        print(response)
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

