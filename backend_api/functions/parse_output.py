def parse_input_text(input_text):
    # Remove any leading or trailing whitespace
    input_text = input_text.strip()

    # Split the input text by the newline character
    lines = input_text.split('\n')

    # Initialize an empty list to store the parsed data
    parsed_data = []

    # Iterate over each line
    for line in lines:
        # Remove the square brackets and split the line by comma
        line = line.strip('[]')
        line_data = line.split(',')

        # Remove any leading or trailing whitespace from each item
        line_data = [item.strip() for item in line_data]

        # Append the parsed line data to the result list
        parsed_data.append(line_data)

    return parsed_data