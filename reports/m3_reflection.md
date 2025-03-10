# NYPD Arrest Tracker Reflection 3

**Authors**: Michael Gelfand, Hala Arar, Michael Hewlett

## What has been implemented since milestone 2

- Working date range picker in sidebar
- Apply button for applying filters
- Reset button clears almost everything
- Created proper title and moved filter sidebar button to the right corner
- Fixed layout of pie charts on right side of screen
- Converted crime frequency pie chart to a bar chart
- Placeholder pie and bar charts to signify no data due to too much filtering

## What has not been implemented and why

- Density plot: Removed as it would make the dashboard too cluttered.
- Month slider: incorporated into the date selector.

## What is not working properly

- The reset button currently does not unselect the region from the map chart. Instead the only way to unselect a region is by clicking on the white area outside of the map. We have tried to implement this but it is proving difficult and will be fixed next milestone.
- We would like to have the map appear greyed out entirely when the filters result in empty dataframes. Current attempts resulted in it resetting the pie charts to show defaults instead of empty placeholders. Will be fixed next milestone.

## What the dashboard does well
- Interactivity and flexibility: The dashboard offers various filters (such as date range and crime type) that allow users to drill down into specific data, providing a tailored view of arrests and crime trends.
- Visualization clarity: The layout and charts are visually appealing, with clear demarcations for arrest data by region, gender, age, and crime type.
- User Experience: The widgets and interactive elements are easy to use, with filters, pie charts, and bar charts all working smoothly.

## Dashboard limitations
- Excessive White Space: There is too much unused space, particularly around the charts and visual elements. This makes the dashboard feel less compact and less efficient.
- Reset Button Does Not Function: The reset button is not properly clearing all selected filters and is not unselecting regions on the map.
- Slider Bar Animation Missing: The transition for the slider bar is not animated, which makes the UI feel static and less interactive.
- Filters Visibility: The filter panel is not prominent enough on the landing page, and its placement needs to be more noticeable to ensure users can find it easily.
- Font Overlapping in Filters: The fonts in the filter options are overlapping, which affects readability and the overall user experience.


## Potential future improvements and additions
- Fix Reset Functionality: Address the issues with the reset button so it properly clears all selections, including unselecting map regions.
- Map Grey-Out Feature: When the filters result in an empty dataset, the map should grey out to indicate no available data, providing better visual feedback to the user.
- Improve Overall Layout: Address the white space issue and improve the overall arrangement of the elements to create a more compact and efficient layout.
- Add Sidebar Transitions: Implement transitions for the sidebar so that it smoothly slides in from the left side of the screen, making the UI feel more dynamic.
- Move Filters to One Corner: Relocate the filter panel to one corner of the screen to optimize space, and allow the filter panel to slide in and out for better interactivity.
- Make Sidebar Semi-Transparent: Adding a slight transparency to the sidebar would create a modern and clean look, enhancing the overall aesthetic of the dashboard.
