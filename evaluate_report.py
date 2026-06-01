
import argparse
import json
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

def load_api_key():
    """Loads the Google AI API key from a .env file."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")
    genai.configure(api_key=api_key)

def read_file_content(file_path):
    """Reads the content of a file and returns it as a string."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def evaluate_metric(prompt, report_content, transcript_content=None):
    """
    Calls the Gemini API to evaluate a specific metric.

    Args:
        prompt (str): The evaluation prompt for the model.
        report_content (str): The content of the technical report.
        transcript_content (str, optional): The source transcript for factual accuracy.

    Returns:
        dict: A dictionary containing the 'score' and 'justification'.
    """
    model = genai.GenerativeModel('gemini-pro-latest')
    full_prompt = prompt
    if transcript_content:
        full_prompt += f"\n\nSource Transcript:\n{transcript_content}"
    full_prompt += f"\n\nTechnical Report:\n{report_content}"

    try:
        response = model.generate_content(full_prompt)
        # Clean the response to extract only the JSON part
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_response)
        return {
            "score": int(result.get("score", 0)),
            "justification": result.get("justification", "No justification provided.")
        }
    except (json.JSONDecodeError, ValueError, Exception) as e:
        print(f"Error processing API response: {e}")
        return {"score": 0, "justification": f"Failed to evaluate due to an error: {e}"}

def main():
    """Main function to orchestrate the evaluation process."""
    try:
        load_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        return

    parser = argparse.ArgumentParser(description="Evaluate a technical report using the Gemini API.")
    parser.add_argument("report_file", help="Path to the technical report file.")
    parser.add_argument("transcript_file", help="Path to the source transcript file.")
    args = parser.parse_args()

    try:
        report_content = read_file_content(args.report_file)
        transcript_content = read_file_content(args.transcript_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    evaluation_metrics = {
        "Clarity and Coherence": """
            As an Academic Reviewer, evaluate the clarity and coherence of the following report. 
            Is the language clear and unambiguous? Does the document flow logically from one section to the next? 
            Return a JSON object with 'score' (integer 1-10) and 'justification' (string).
        """,
        "Factual Accuracy": """
            As a Fact-Checker, you will be given a source transcript and a technical report. 
            Your task is to verify the factual accuracy of the report against the transcript. 
            Identify any discrepancies. Return a JSON object with 'score' (integer 1-10) and 'justification' (string) listing any errors found.
        """,
        "Depth of Analysis": """
            As a University Professor, assess the depth of analysis in this report. 
            Does it offer critical insights, implications, or connections to broader themes as a graduate-level document should? 
            Return a JSON object with 'score' (integer 1-10) and 'justification' (string).
        """,
        "Structural Adherence": """
            As an Academic Journal Editor, evaluate the report's adherence to a formal academic structure. 
            Is it well-formatted and does it contain all the necessary components of a technical report (e.g., Title, Abstract, logical sections)? 
            Return a JSON object with 'score' (integer 1-10) and 'justification' (string).
        """
    }

    results = {}
    total_score = 0

    print("Starting evaluation...")
    for metric, prompt in evaluation_metrics.items():
        print(f"Evaluating: {metric}...")
        is_accuracy_check = metric == "Factual Accuracy"
        result = evaluate_metric(
            prompt,
            report_content,
            transcript_content if is_accuracy_check else None
        )
        results[metric] = result
        total_score += result["score"]
        time.sleep(60)  # Wait for 60 seconds to avoid rate limiting
    print("Evaluation complete.")

    average_score = total_score / len(evaluation_metrics) if evaluation_metrics else 0

    # Console Output
    print("\n--- Evaluation Results ---")
    for metric, result in results.items():
        print(f"\nMetric: {metric}")
        print(f"  Score: {result['score']}/10")
        print(f"  Justification: {result['justification']}")
    print("\n--------------------------")
    print(f"Overall Average Score: {average_score:.2f}/10")
    print("--------------------------\n")

    # File Output
    output_filename = "evaluation_results.md"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("# AI-Generated Report Evaluation Results\n\n")
        f.write(f"This document presents the automated evaluation of the technical report located at `{args.report_file}`.\n\n")
        f.write(f"**Overall Average Score: {average_score:.2f}/10**\n\n")
        f.write("---\n\n")
        for metric, result in results.items():
            f.write(f"## {metric}\n\n")
            f.write(f"**Score:** {result['score']}/10\n\n")
            f.write(f"**Justification:**\n")
            f.write(f"> {result['justification']}\n\n")
            f.write("---\n\n")

    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()
