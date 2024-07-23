Creating FL-App
  •	Firstly, we are selecting a list of practice areas to be listed in the page
  •	We are making a connection to the database, every time when the practice areas, states or city is selected, 
  •	The connection is made to extract the data
  •	Also, to remember the data selected, a cache is created, which is a python dictionary that stores the practice area, state and the city selected
  •	Basically we have 5 pages 
    	Main Page (‘/’) - Which will display all the practice areas listed
    	States Page(‘/state’) – Which will display all the states matching to the practice area selected
    	City Page('/city’) – Which will display all the cities match to the practice area and state selected
    	Law firms Page(‘/law_firms’) – Which will display all the law firms matching to the city, state and practice area, In additional it also displays the law firms matching with the state selected as suggestions
    	Specific law page(‘/LawPage) – This page will display all the details about the selected law firm
    
