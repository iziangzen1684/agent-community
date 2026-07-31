# agent-community
A very simple chat room simulator using LLM.

# Quickstart
```sh
git clone https://github.com/iziangzen1684/agent-community
cd agent-community
python -m venv .venv
pip install -r requirements.txt
cp config_tempt.json config.json
```
Then edit config.json:
```json
{
  "api_key": "sk-**",
  "model" : "example-10b",
  "base_url": "https://api.example.ai/v1"
}
```
Then run main.py:
```sh
python main.py
```
Have fun =)
