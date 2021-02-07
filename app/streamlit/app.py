import test_main
import data_entry
import data_update 
import data_delete 
import company_situation_analysis 

from multiapp import MultiApp
app = MultiApp()
app.add_app("Main Demo App", test_main.app)
app.add_app("Data Entry", data_entry.app)
app.add_app("Updating Data", data_update.app)
app.add_app("Deleting Data", data_delete.app)
app.add_app("Company Situation Analysis", company_situation_analysis.app)
app.run()