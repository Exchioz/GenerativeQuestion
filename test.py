data ={
    "multiple_choices": [
        {
            "question": "Kapan penemuan transistor terjadi yang mengarah pada pengembangan komputer generasi pertama yang lebih kecil, lebih cepat, dan lebih efisien energi?",
            "option_a": "1947",
            "option_b": "1950",
            "option_c": "1970",
            "option_d": "1980",
            "answer": "A",
            "category": "test",
            "level": "C2"
        }
    ]
}

get_type = list(data.keys())[0]
category = data[get_type][0]

print(type(category))
print(category)