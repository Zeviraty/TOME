import json

TELNET_COMMANDS = {
    # Telnet command bytes (RFC 854)
    "IAC":   bytes([255]),  # Interpret As Command
    "DONT":  bytes([254]),  # Dont (Server)
    "DO":    bytes([253]),  # Do   (Server)
    "WONT":  bytes([252]),  # Wont (Client)
    "WILL":  bytes([251]),  # Will (Client)
    "SB":    bytes([250]),  # Subnegotiation Begin
    "GA":    bytes([249]),  # Go ahead
    "EL":    bytes([248]),  # Erase line
    "EC":    bytes([247]),  # Erase character
    "AYT":   bytes([246]),  # Are you there
    "AO":    bytes([245]),  # Abort output
    "IP":    bytes([244]),  # Interrupt process
    "BREAK": bytes([243]),  # Break
    "DM":    bytes([242]),  # Data mark
    "NOP":   bytes([241]),  # No operation
    "SE":    bytes([240]),  # Subnegotiation End

    # Telnet options (partial list, per IANA assignments)
    "BINARY":              bytes([0]),
    "ECHO":                bytes([1]),
    "SUPPRESS_GO_AHEAD":   bytes([3]),
    "STATUS":              bytes([5]),
    "TIMING_MARK":         bytes([6]),
    "TERMINAL_TYPE":       bytes([24]),
    "NAWS":                bytes([31]),   # Negotiate About Window Size
    "TERMINAL_SPEED":      bytes([32]),
    "REMOTE_FLOW_CONTROL": bytes([33]),
    "LINEMODE":            bytes([34]),
    "ENVIRON":             bytes([36]),

    # Common MUD extensions
    "GMCP":  bytes([201]),  # Generic Mud Communication Protocol
    "ATCP":  bytes([200]),  # Achaea Telnet Client Protocol (Inferior to GMCP)
    "MSDP":  bytes([69]),   # MUD Server Data Protocol (Implemented in GMCP)
    "MSSP":  bytes([70]),   # MUD Server Status Protocol

    # MSSP
    "MSSP_VAR": bytes([1]), # MSSP variable
    "MSSP_VAL": bytes([2]), # MSSP value

}

INVERSE_TELNET = {v: k for k, v in TELNET_COMMANDS.items()}
INVERSE_TELNET[bytes([1])] = "ECHO"
del INVERSE_TELNET[bytes([2])]

def send(client, content: str = "") -> None:
    message: bytes = b""
    if client.debug == True:
        client.send("Sending telnet commands: "+content)
    for i in content.replace("\\","").split(" "):
        if i in TELNET_COMMANDS.keys():
            message += TELNET_COMMANDS[i]
        else:
            message += i.encode()
    try:
        client.bsend(message)
    except (BrokenPipeError, OSError):
        client.disconnect()

def get(client) -> dict:
    data = client.bget()
    gmcp_data = {}
    telnet_log = []

    i = 0
    while i < len(data):
        byte = data[i]

        if byte == TELNET_COMMANDS["IAC"][0]:
            i += 1
            if i >= len(data): break

            cmd = data[i]
            cmd_byte = bytes([cmd])
            cmd_name = INVERSE_TELNET.get(cmd_byte, f"UNKNOWN({cmd})")

            # Handle subnegotiation: IAC SB GMCP ... IAC SE
            if cmd == TELNET_COMMANDS["SB"][0] and i + 1 < len(data) and data[i + 1] == TELNET_COMMANDS["GMCP"][0]:
                i += 2  # Skip SB and GMCP
                start = i
                while i < len(data) - 1:
                    if data[i] == TELNET_COMMANDS["IAC"][0] and data[i + 1] == TELNET_COMMANDS["SE"][0]:
                        payload = data[start:i].decode(errors="ignore")
                        if " " in payload:
                            key, value = payload.split(" ", 1)
                            try:
                                gmcp_data[key] = json.loads(value)
                            except json.JSONDecodeError:
                                gmcp_data[key] = value
                        else:
                            gmcp_data[payload] = None
                        telnet_log.append(f"IAC SB GMCP {payload} IAC SE")
                        i += 2  # Skip IAC SE
                        break
                    i += 1
                continue

            # Handle WILL/WONT GMCP
            elif cmd in [TELNET_COMMANDS["WILL"][0], TELNET_COMMANDS["WONT"][0], TELNET_COMMANDS["DO"][0], TELNET_COMMANDS["DONT"][0]] and i + 1 < len(data):
                option = data[i + 1]
                if option == TELNET_COMMANDS["GMCP"][0]:
                    gmcp_data["gmcp"] = (cmd == TELNET_COMMANDS["WILL"][0] or cmd == TELNET_COMMANDS["DO"][0])
                    telnet_log.append(f"IAC {cmd_name} GMCP")
                    i += 2
                    continue
                else:
                    option_name = INVERSE_TELNET.get(bytes([option]), f"UNKNOWN({option})")
                    telnet_log.append(f"IAC {cmd_name} {option_name}")
                    i += 2
                    continue

            # Handle other commands with options (e.g., DO NAWS)
            elif i + 1 < len(data):
                option = data[i + 1]
                option_name = INVERSE_TELNET.get(bytes([option]), f"UNKNOWN({option})")
                telnet_log.append(f"IAC {cmd_name} {option_name}")
                i += 2
                continue

            else:
                telnet_log.append(f"IAC {cmd_name}")
                i += 1

        else:
            telnet_log.append(str(byte))
            i += 1

    if telnet_log:
        gmcp_data["telnet"] = telnet_log
    if client.debug == True:
        client.send("telnet_log: "+str(telnet_log))

    return gmcp_data
