# NYPD Arrest Tracker App Proposal

**Authors**: Michael Gelfand, Hala Arar, Michael Hewlett

## What has been implemented

- Map of NYC showing precincts/boroughs with hover tool tips and clickable
- Chart for relative frequency of crime type
- Pie chart for gender
- Pie chart for age
- Sidebar for advanced filters
- Toggle for map to display precinct/borough
- Dropdown menu filtering by crime type

## What has not been implemented and why

## What was implemented differently and why

- Chart for relative frequency of crime type: We intended to implement this as a bar chart but had difficulties so we have implemented it as a pie chart

## Known bugs

- Sidebar expanding does not shift the main content over, instead it covers the content
- Null value present in crime type filter
- Reset charts button only resets charts, not the map, which can lead to a misleading display

## Deviations from 531 best practices

## What the dashboard does well

- Does not overwhelm a user with information. Since our target group are executive leadership, they need streamlined information.
- Uses an appropriate colour intensity scale for the map display and differently colours for the chart display to intuitively reflect the continuous/categorical nature of each chart type.

## Dashboard limitations

- Layout needs to fit onto window without needed to scroll down
- Sidebar button ('☰') should be in the furthest left column to follow common UI design patterns

## Potential future improvements and additions

Chart reset button

- Currently only resets borough/precinct selection, not crime type selection. We need to think through the user flow for resetting charts in general, e.g. to what extent we want them to reset individual charts vs resetting everything.

Crime type filter

- Displaying crime types as a grid of checkboxes. Right now the dropdown menu is a clunky UI.
- Display crime types using 'Sentence case'
- Make it more clear in the main display what crime types have been selected in the filter
- Make the option to 'clear all' selected crime types more obvious
- Add function to sort crime types in selection display by frequency

Pie charts

- Hover over percentage should match rounding to 1 decimal place
- For gender and age, those categories should be displayed without the hover - e.g. the gender pie chart should have "Male" and "Female" printed without needing to hover