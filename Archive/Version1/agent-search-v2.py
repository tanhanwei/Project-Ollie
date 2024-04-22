import requests
from googlesearch import search
from newspaper import Article

search_query = "top camera in 2024"
num_results = 3

search_results = search(search_query, num_results=num_results, advanced=True)

for i, result in enumerate(search_results, start=1):
    url = result.url
    
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        main_content = article.text
        
        output_file = f"result_{i}.txt"
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(main_content)
        
        print(f"Content saved to {output_file}.")
    
    except Exception as e:
        print(f"Error processing URL: {url}")
        print(f"Error message: {str(e)}")