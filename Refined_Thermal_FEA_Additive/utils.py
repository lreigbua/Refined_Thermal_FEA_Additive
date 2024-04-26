def read_json_file(json_file_path): 
    #returns a dictionary of the data in the path given
    import json
 
    # Opening JSON file
    f = open(json_file_path)
    
    # returns JSON object as 
    # a dictionary
    return json.load(f)