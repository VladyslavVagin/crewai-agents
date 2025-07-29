#!/usr/bin/env python
import os
import warnings

from financial_researcher.crew import FinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


os.makedirs('output', exist_ok=True)

def run():
    """
    Run the research crew.
    """
    inputs = {
        'company': 'Apple'
    }

    # Create and run the crew
    result = FinancialResearcher().crew().kickoff(inputs=inputs)
    print(result.raw)
    
    
if __name__ == "__main__":
    run()
