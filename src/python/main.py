from ai_powered_py.AI_POWER import AI_POWER
import argparse



def main():
    parser = argparse.ArgumentParser(description='A simple script that makes an interface between CLI and AI_POWER lib.')
    parser.add_argument(
        "--logs_file",
        type=str,
        required=True,
        help="Path to the logs file."
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="Q",
        help="Mode of the AI : [Q]uick or [D]eep."
    )
    parser.add_argument(
        "--last_command",
        type=str,
        required=True,
        help="Last command executed."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mistral",
        help="Model to use (default: mistral)."
    )
    parser.add_argument(
        "--debug",
        type=int,
        default=0,
        help="Debug level 0 or 1."
    )

    args = parser.parse_args()
    AI_OBJECT = AI_POWER(
        logs_file=args.logs_file,
        mode=args.mode,
        last_command=args.last_command,
        model=args.model,
        debug=args.debug
    )
    AI_OBJECT.buildObject()
    AI_OBJECT.runModel()



if __name__=="__main__":
    main()