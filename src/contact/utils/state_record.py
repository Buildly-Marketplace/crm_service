from datetime import datetime

from contact.models import StateRecord, Address


class StateRecordUtil:
    def __init__(self, state_record=None):
        self.state_record = state_record

    def process_state_file(self, uploaded_file):
        try:
            processed_count = 0
            error_count = 0
            errors = []
            for chunk in self.file_parser(uploaded_file, chunk_size=1000):
                records = []
                for data_parts in chunk:
                    try:

                        records.append(StateRecord(**self.get_state_record(data_parts)))
                    except Exception as e:
                        error_count += 1
                        errors.append({"line": data_parts, "error": str(e)})

                # Perform bulk_create for the chunk
                StateRecord.objects.bulk_create(records, batch_size=1000)
                processed_count += len(records)
            return {
                'processed_count': processed_count,
                'error_count': error_count,
                'errors': errors
            }

        except Exception as e:
            print(e)
            return

    @staticmethod
    def file_parser(file, chunk_size=1000):
        buffer = []
        for line in file:
            decoded_line = line.decode('utf-8').strip()
            if not decoded_line:
                continue
            buffer.append(decoded_line.split('\t'))  # Process and add to the buffer
            if len(buffer) >= chunk_size:
                yield buffer
                buffer = []  # Reset buffer
        if buffer:
            yield buffer

    @staticmethod
    def get_state_record(data):

        # Parse the address into an Address dictionary
        import re

        # Extract the address parts
        address_line = data[7].strip()
        city = data[9].strip()
        state = data[0][:2]
        zip_code = data[11]

        # Use regex to break down the address
        pattern = (r"(?P<street_num>\d+)\s*(?P<street_dir>\w+)?\s+"
                   r"(?P<street_name>[\w\s]+?)\s+(?P<street_type>\w+)")
        address_parts = re.match(pattern, address_line)

        address_dict = {
            "street_num": address_parts.group("street_num") if address_parts else None,
            "street_dir": address_parts.group("street_dir") if address_parts else None,
            "street_name": address_parts.group("street_name").strip() if address_parts else None,
            "street_type": address_parts.group("street_type") if address_parts else None,
            "city": city,
            "zip_code": zip_code,
        }
        # save address
        address = Address.objects.create(**address_dict)

        # Output both dictionaries
        print("Address:", address_dict)
        return {
            "type": "Person",
            "original_state": state,  # 'ALA' -> 'AL'
            "precinct": data[1][:6],  # Voter Precinct
            "last_name": data[2],  # Last Name
            "suffix": data[3],  # Suffix (empty in this case)
            "first_name": data[4],  # First Name
            "middle_name": data[5],  # Middle Name
            "voter_id": data[1],  # Voter ID
            "political_affiliation": data[24],  # 'REP'
            "status": "A" if data[28] == "ACT" else "I",  # 'ACT' -> Active
            "date_of_birth": datetime.strptime(data[21], '%m/%d/%Y').strftime('%Y-%m-%d'),
            "registration_date": datetime.strptime(data[22], '%m/%d/%Y').strftime('%Y-%m-%d'),
            "residential_address": address,  # Referencing the parsed address
            "county_desc": "Alachua",  # Assuming Gainesville belongs to Alachua county
            "returned_undeliverable": False,
            "voter_history": {  # Placeholder for custom JSON data
                "elections": [
                    {"year": 2020, "participation": "Yes"},
                    {"year": 2018, "participation": "No"},
                ]
            },
        }
