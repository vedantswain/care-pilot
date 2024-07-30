'''
Generate messages to recruit participants.
Message content changes based on the medium of recruitment (e.g., Reddit, LinkedIn, Email, etc.)
'''

# Define your template
templates = {
    'r':
"""
Hi {username},  

I’m a researcher from Northeastern University focused on worker wellbeing. I saw you discuss challenges with customer interaction on {forum}. Customers uncivil behavior is a real problem, and my team is studying how AI can help workers deal with this challenge.

We’re looking for people like you to test our AI prototype in a paid remote study. The study lasts 90 minutes and includes user testing, interviews, and design brainstorming. Sessions will be scheduled at your convenience. We will record the audio and screen of your session for analysis. You can earn up to $50 in an Amazon Gift card.

Your insights will help shape future AI tools for emotional resilience and job satisfaction.

If you’re interested, visit: https://propilot.khoury.northeastern.edu/

Let me know if you have any questions.

Thanks, 
{name} 
{position}
Khoury College of Computer Sciences, Northeastern University 
{websitelink} 
"""
}

def get_params_from_template(template):
    """
    Extract parameters from the template string.
    """
    params = []

    # Remove all punctuation from the template string
    template = template.replace(",", "").replace(".", "").replace(":", "").replace(";", "").replace("!", "").replace("?", "")

    for word in template.split():
        if word.startswith("{") and word.endswith("}"):
            params.append(word[1:-1])
    return params

if __name__ == "__main__":
    """
    Researcher needs to input their name, position, and website.link. 
    """
    print("Please input the following information to generate the recruitment message:")

    message_params = {}

    message_params["name"] = input("Name: ")
    if message_params["name"] == "":
        message_params["name"] = "Vedant Das Swain"
    message_params["position"] = input("Position: ")
    if message_params["position"] == "":
        message_params["position"] = "Distinguised Postdoctoral Fellow"
    message_params["websitelink"] = input("Website Link: ")
    if message_params["websitelink"] == "":
        message_params["websitelink"] = "https://vedantswain.com/"

    """
    Fix the medium of recruitment to generate the message.
    """
    print()
    while True:
        medium = input("Enter the medium of recruitment ([r]eddit, [l]inkedIn, [e]mail):")
        if medium not in templates:
            print("Invalid medium. Please enter 'r' for Reddit, 'l' for LinkedIn, or 'e' for Email.")
        else:
            break

    template = templates[medium]

    """
    Seek user input for the username, forum, and screener link.
    """
    all_params = get_params_from_template(template)
    participant_params = [param for param in all_params if param not in ["name", "position", "websitelink"]]
    print(participant_params)

    while True:
        for param in participant_params:
            if medium == "r" and param == "forum":
                link_forum = input("Forum Link: ")
                if link_forum != "" or param not in message_params.keys():
                    message_params[param] = "r//"+link_forum.split("/")[4]
            else:
                message_params[param] = input(param+": ")

        generated_message = template.format(**message_params)
        print(generated_message)
        print()