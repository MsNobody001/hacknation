import os
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage
import json

sys.path.append(str(Path(__file__).parent))

from accident_data_collector_agent import AccidentDataCollectorAgent

from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 60)
    print("Wpisz 'quit' aby zakończyć")
    print("=" * 60)
    print()
    
    agent = AccidentDataCollectorAgent()
    
    chat_history = []
    
    print("Asystent: Witam. Jestem gotowy do przyjęcia zgłoszenia wypadku.")
    print("          Proszę opowiedzieć co się stało.\n")
    
    while True:
        user_input = input("Ty: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'koniec', 'wyjście']:
            print("\n" + "=" * 60)
            print("FINALNE ZEBRANE DANE:")
            print("=" * 60)
            data = agent.get_collected_data()
            print(json.dumps(data.model_dump(), indent=2, ensure_ascii=False))
            print("=" * 60)
            print("Dziękuję za rozmowę. Do widzenia!")
            break
        
        
        try:
            bot_response = agent.collect_data(user_input, chat_history)
            
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=bot_response))
            
            print(f"\nAsystent: {bot_response}\n")
            
            missing = agent.collected_data.get_missing_required_fields()
            if not missing:
                print(f"  [Wszystkie wymagane dane zebrane!]")
                print(f"\n{'='*60}")
                print("ZEBRANE DANE:")
                print(f"{'='*60}")
                data = agent.get_collected_data()
                print(json.dumps(data.model_dump(), indent=2, ensure_ascii=False))
                print(f"{'='*60}\n")
            print()
            
        except Exception as e:
            print(f"\nBłąd: {e}\n")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
