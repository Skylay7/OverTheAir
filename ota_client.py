import socket
import json
from protocol import Protocol


def main():
    client_socket = socket.socket()
    client_socket.connect(Protocol.SERVER)
    print(f"Connected to {Protocol.SERVER[0]} on port {Protocol.SERVER[1]}...")

    data = Protocol.get_analyzed_data(client_socket)
    command_list = display_welcome_message(data)
    interact_with_server(client_socket, command_list)

    client_socket.close()


def display_welcome_message(data):
    data = json.loads(data)
    print("Commands Available:")
    available_commands = list({cmd["args"][0] for cmd in data["available_commands"].values()})
    for cmd, details in data["available_commands"].items():
        print(f"{cmd}: {details['description']} - Args: {' '.join(details['args'])}")
    print("quit: Quits program and ends connection. - Args: QUIT")
    return available_commands


def interact_with_server(client_socket, command_list):
    while (client_input := input("Enter Command: ")) != "QUIT":
        command = client_input.split(" ")
        if command[0] not in command_list:
            print("Error: Command does not exist.")
            continue

        if command[0] == "UPDATE_FUNCTIONS":
            args = " ".join(command[1:])
        else:
            args = command[1:]
        json_dict = {"command": command[0], "args": args}
        message = json.dumps(json_dict)
        send_command(client_socket, message)

        response = Protocol.get_analyzed_data(client_socket)
        if command[0] == "UPDATE_FUNCTIONS" and "success" in response.decode():
            command_name = json.loads(args)["command"][0]
            command_list.append(command_name)
            print(response)
        elif command[0] == "TAKE_SCREENSHOT":
            with open("new_screenshot.png", "wb") as screenshot:
                screenshot.write(response)
        else:
            print(response)
    send_command(client_socket, client_input)


def send_command(client_socket, client_input):
    message = Protocol.create_message(client_input.encode())
    client_socket.send(message)


if __name__ == '__main__':
    main()
