import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import pandas as pd
import plotly
import plotly.plotly as py
import plotly.figure_factory as ff

from datetime import datetime
from datetime import timedelta

from dateutil.parser import parse
import datetime



app = dash.Dash()

app.scripts.config.serve_locally = True


SEQUENCE_COLUMN = '1. N'
TASK_NAME_COLUMN = '2. Task name'
EXPECTED_START_DATE_COLUMN = '3. Expected start date'
EXPECTED_END_DATE_COLUMN = '4. Expected end date'
ACTUAL_START_DATE_COLUMN = '5. Actual start date'
ACTUAL_END_DATE_COLUMN = '6. Actual end date'
TASK_EXPECTED_DURATION_COLUMN = '7. Expected duration'
TASK_ACTUAL_DURATION_COLUMN = '8. Actual duration'

DF_SIMPLE = pd.DataFrame({
		SEQUENCE_COLUMN: ['1', '2', '3', '4', '5', '6', "7", "8", "9"],
		TASK_NAME_COLUMN: ['Find a new hobby', 'Purchase equipment', 'Wait for good weather', 'Hire an airplane', 'Jump from with parachute', 'Come out of coma', "", "", ""],
		EXPECTED_START_DATE_COLUMN: ['29/03/2018', '29/03/2018', '30/03/2018', '30/03/2018', '05/04/2018', '05/04/2018', "", "", ""],
		EXPECTED_END_DATE_COLUMN: ['29/03/2018', '29/03/2018', '05/04/2018', '31/03/2018', '05/04/2018', '05/05/2018', "", "", ""],
		ACTUAL_START_DATE_COLUMN: ['29/03/2018', '29/03/2018', '30/03/2018', '30/03/2018', '02/04/2018', '02/04/2018', "", "", ""],
		ACTUAL_END_DATE_COLUMN: ['29/03/2018', '30/03/2018', '02/04/2018', '01/04/2018', '02/04/2018', '10/07/2025', "", "", ""],
		TASK_EXPECTED_DURATION_COLUMN: ["", "", "", "", "", "", "", "", ""],
		TASK_ACTUAL_DURATION_COLUMN: ["", "", "", "", "", "", "", "", ""]
})


# DF_SIMPLE = pd.DataFrame({
#     SEQUENCE_COLUMN: ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
#     TASK_NAME_COLUMN: ["", "", "", "", "", "", "", "", ""],
#     EXPECTED_START_DATE_COLUMN: ["", "", "", "", "", "", "", "", ""],
#     EXPECTED_END_DATE_COLUMN: ["", "", "", "", "", "", "", "", ""],
#     ACTUAL_START_DATE_COLUMN: ["", "", "", "", "", "", "", "", ""],
#     ACTUAL_END_DATE_COLUMN: ["", "", "", "", "", "", "", "", ""],
#     TASK_ACTUAL_DURATION_COLUMN: ["", "", "", "", "", "", "", "", ""],
#     TASK_EXPECTED_DURATION_COLUMN: ["", "", "", "", "", "", "", "", ""]
# })

mDataFrame = DF_SIMPLE.to_dict('records')

title = html.H1("Project Management Tool", style={'color':'purple', 'fontFamily':'calibri','font-weight':'strong','font-weight':'bold','fontSize': 46,"textAlign":'center','marginTop': 20,'marginBottom': 60,}, className='row')
description = html.P ("Welcome to our Project Management Tool which will help you to visualize your project. To construct your gantt chart please insert the dates in the following format: dd/mm/yyyy",
  style={'color':'black', 'fontFamily':'calibri','font-weight':'bold',"textAlign":'left','marginLeft':10}, className='row')

table = dt.DataTable(
        rows=mDataFrame,
				sortable=False,
        editable=True,
        id='editable_table'
    )

app.layout = html.Div([
    title,
    description,
    html.Div([table, html.Button('Add Task', id='button', style={'width':'100%','marginTop': 5,})], style={'marginTop': 25, 'marginLeft':10}, className='row'),
    html.Div([dcc.Graph(id="graph")],style={'marginBottom': 50, 'marginTop': 25,'width':'100%'}, id="graph_container", className='row')
], className='row')


@app.callback(
    Output('editable_table', 'rows'),
    [Input('button', 'n_clicks')])
def update_output(n_clicks):
	mDataFrame.append({
			SEQUENCE_COLUMN:str(len(mDataFrame)+1),
			TASK_NAME_COLUMN:"", 
			EXPECTED_START_DATE_COLUMN:"",
			EXPECTED_END_DATE_COLUMN:"",
			ACTUAL_START_DATE_COLUMN:"", 
			ACTUAL_END_DATE_COLUMN:"",
      TASK_EXPECTED_DURATION_COLUMN: "",
      TASK_ACTUAL_DURATION_COLUMN: ""
      })
	return mDataFrame

@app.callback(
    Output('graph_container', 'children'),
    [Input('editable_table', 'rows')])
def update_figure(rows):	
   	global DF_SIMPLE
   	global mDataFrame
   	global table
   	DF_SIMPLE = pd.DataFrame(rows)
   	expectedDF = []
   	actualDF = []

   	for lab, row in DF_SIMPLE.iterrows():
   		taskName = 'Task ' + row[SEQUENCE_COLUMN]
   		expectedStartDate = row[EXPECTED_START_DATE_COLUMN]
   		expectedEndDate = row[EXPECTED_END_DATE_COLUMN]
   		if(isValidDate(expectedStartDate) and isValidDate(expectedEndDate)):
   			expectedDuration= calculateDuration(expectedStartDate, expectedEndDate)
   			validStartDate = datetime.datetime.strptime(expectedStartDate, "%d/%m/%Y").strftime("%Y-%m-%d")
   			validEndDate =datetime.datetime.strptime(expectedEndDate, "%d/%m/%Y").strftime("%Y-%m-%d") + ' 23:59:59'
   			expectedDF.append(dict(Task=taskName, Start = validStartDate, Finish = validEndDate, Resource= row[TASK_NAME_COLUMN]))
   			row[TASK_EXPECTED_DURATION_COLUMN] = expectedDuration
   		else:
   			row[TASK_EXPECTED_DURATION_COLUMN] = ""
        
   		actualStartDate = row[ACTUAL_START_DATE_COLUMN]
   		actualEndDate = row[ACTUAL_END_DATE_COLUMN]
   		if(isValidDate(actualStartDate) and isValidDate(actualEndDate)):
   			actualDuration = calculateDuration(actualStartDate, actualEndDate)
   			validStartDate = datetime.datetime.strptime(actualStartDate, "%d/%m/%Y").strftime("%Y-%m-%d")
   			validEndDate =datetime.datetime.strptime(actualEndDate, "%d/%m/%Y").strftime("%Y-%m-%d") + ' 23:59:59'
   			actualDF.append(dict(Task=taskName, Start = validStartDate, Finish = validEndDate,  Resource= row[TASK_NAME_COLUMN]))
   			row[TASK_ACTUAL_DURATION_COLUMN] = actualDuration
   		else:
   			row[TASK_ACTUAL_DURATION_COLUMN] =""



   	mDataFrame = DF_SIMPLE.to_dict('records')
   	#setTableValue(mDataFrame)
   	expectedRoadmap = dcc.Graph(id="expected_gantt_chart")
   	actualRoadmap = dcc.Graph(id="actual_gantt_chart")
   	expectedRoadmapDiv = html.Div([], className = 'six columns')
   	actualRoadmapDiv = html.Div([], className = 'six columns')
   	if len(expectedDF)>0:
   		expectedFigure = ff.create_gantt(expectedDF, title='Expected Project Roadmap')
   		expectedRoadmap.figure = expectedFigure
   		expectedRoadmapDiv.children = expectedRoadmap
   	
   	if len(actualDF)>0:
   		actualFigure = ff.create_gantt(actualDF, title='Actual Project Roadmap')
   		actualRoadmap.figure = actualFigure
   		actualRoadmapDiv.children = actualRoadmap

   	result = html.Div([expectedRoadmapDiv, actualRoadmapDiv], className = 'row')

   	return result


def isValidDate(date_text):
    try: 
        datetime.datetime.strptime(date_text, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def calculateDuration(startTime, endTime):
	date_format = "%d/%m/%Y"
	a = datetime.datetime.strptime(startTime, date_format)
	b = datetime.datetime.strptime(endTime, date_format)
	delta = b - a
	days = delta.days
	if days ==0:
		result = '1 day'
	else: 
		result = str(days+1) + ' days'
	return result

def setTableValue(updatedRows):
	table.rows = updatedRows


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server()