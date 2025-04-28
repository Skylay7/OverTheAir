import socket
import functions
import json
from protocol import Protocol


def handle_client(client_socket):
    while True:
        try:
            data = Protocol.get_analyzed_data(client_socket)
        except Exception as e:
            print("Client disconnected:", e)
            break
        if not data or data.decode() == "QUIT":
            break

        message = handle_response(data)
        if message:
            try:
                sent_bytes = client_socket.send(message)
                if sent_bytes == len(message):
                    print("Response sent successfully.")
            except Exception as e:
                print("Error sending response:", e)
                break

    client_socket.close()
    print("Connection closed.")


def handle_response(json_data):
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return Protocol.create_message(f"Invalid JSON syntax: {e}".encode())

    command_name = data.get("command")
    args = data.get("args", [])

    if command_name == "UPDATE_FUNCTIONS":
        return handle_update_functions(args)
    elif command_name in functions.function_dict:
        return handle_custom_command(command_name, args)
    else:
        return Protocol.create_message("Error: Command not found.".encode())


def handle_update_functions(args):
    try:
        func_json = json.loads("".join(args))
        result_message = update_functions(func_json)
        print(result_message)
        return Protocol.create_message(result_message.encode())
    except json.JSONDecodeError as e:
        return Protocol.create_message(f"Invalid JSON syntax: {e}".encode())
    except Exception as e:
        print("Update function error:", e)
        return Protocol.create_message("Error updating function.".encode())


def handle_custom_command(command_name, args):
    try:
        func = functions.function_dict[command_name]
        result = func(*args)
        if not isinstance(result, bytes):
            result = result.encode()
        return Protocol.create_message(result)
    except TypeError as e:
        return Protocol.create_message(f"Argument error: {e}".encode())
    except Exception as e:
        return Protocol.create_message(f"Error executing command: {e}".encode())


def update_functions(json_data):
    command = json_data.get("command")
    command_name = command[0]
    function_name = json_data.get("function_name")
    description = json_data.get("description")
    code = json_data.get("code")
    try:
        update_func_res = functions.update_functions(code, function_name, command_name)
        add_func_to_welcome_message(command, description)
        return update_func_res
    except SyntaxError as e:
        return f"Syntax error in function definition: {e}"
    except Exception as e:
        return f"Error while adding function: {e}"


def add_func_to_welcome_message(command, description):
    data = {"description": description, "args": command}
    print(data)
    with open("welcome_message.json", "r") as file:
        file_data = json.loads(file.read())
        file_data["available_commands"][command[0]] = data
    with open("welcome_message.json", "w") as file:
        file.write(json.dumps(file_data))
    print(f"Added to welcome message {command[0]}")


def send_welcome_message(client_socket):
    client_socket.send(Protocol.create_message(functions.function_dict["GET_WELCOME_MESSAGE"]()))
    print("Sent Welcome Message")


def main():
    server_socket = socket.socket()
    server_socket.bind(Protocol.SERVER)
    server_socket.listen()
    print(f"Server listening on port {Protocol.SERVER[1]}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Established connection with {addr}")
            send_welcome_message(client_socket)
            handle_client(client_socket)
    except Exception as e:
        print("Server error:", e)
    finally:
        print("Error occurred.")
        server_socket.close()
        print("Server socket closed.")


if __name__ == '__main__':
    main()
