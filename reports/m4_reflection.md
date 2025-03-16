# NYPD Arrest Tracker Reflection 4

**Authors**: Michael Gelfand, Hala Arar, Michael Hewlett

## What has been implemented since milestone 3

- Improved overall layout: 
    - Sidebar transitions: Added smooth transitions for the sidebar so that it now slides in from the left side of the screen, improving the user experience over the previous abrupt appearance.
    - Pie chart layout: Updated the pie charts' arrangement to fit side by side under the bar chart, eliminating unnecessary white space and improving the layout.
    - Collapsible About text: The 'About' section has been converted into a collapsible button to make the interface more compact and user-friendly.

- Enhanced dashboard performance:
    - Data conversion to binary formats: Data has been converted into binary file formats for faster loading and reduced processing time.
    - Eliminating redundant filters: We have cleaned up the data by removing unnecessary filters, which streamlines the process and reduces data processing time.
    - Optimized code: Ensured that no row-wise operations are present in the code, which significantly boosts performance.
    - Function caching: Implemented function caching to prevent re-executing expensive operations unnecessarily, improving performance.

- Map and visual enhancements:
    - Greying out boroughs with no data: Boroughs that do not have data are now greyed out on the map to avoid confusion and improve user experience.
    - Title on the map: Added a dynamic title to the map to indicate whether boroughs or precincts are currently selected, giving users more context.
    - Dropdown overlap issue fixed: Fixed the issue with overlapping dropdown menu options for the crime type filter, making it more user-friendly.
    - Loading indicators: Added loading indicators to both the charts and the map, letting users know that the system is processing their request.
    - Mouse pointer changes: Updated the mouse pointer to change when hovering over clickable components, providing better visual cues for user interactivity.
    - Removed unnecessary chart interactivity: Disabled unnecessary zooming functionality in the bar chart and removed the actions menu (three dots) from the map for a cleaner, more focused user interface.
    - Transparency on filter sidebar: Made the filter sidebar transparent, allowing users to see the underlying visualizations while interacting with the filters.
    - Legend repositioning: Moved the map legend to the left side, optimizing space and making the map clearer to navigate.



## What has not been implemented and why

Chart as cards:
- We had initially considered turning each chart into a card to improve appearance. However, after reviewing the layout and functionality, we decided that the current design is effective enough and that adding cards would not significantly enhance the user experience.

Time-based plot (Density chart):
- We did not implement a time-based plot, such as the density chart, because we believe it would have been too complex given the project's scope. After consulting with Joel, he agreed that this addition would exceed the current goals and would take too much time and resources to implement.

## What is not working properly

- Reset button: The reset button is currently not functioning as intended. It is supposed to reset the filters and date range picker, but this is not working correctly. We discussed the issue with Joel, and he mentioned that implementing this feature would be difficult due to the complexity of resetting multiple components at once.

## What the dashboard does well
- User experience: The dashboard is now more intuitive and user-friendly, with smooth transitions, clear data visualizations, and interactive components that help users navigate through the data efficiently.
- Performance optimization: The caching and data optimizations have drastically improved the performance, and users can now interact with the dashboard without experiencing significant delays.
- Visual clarity: The layout improvements, including the side-by-side pie charts and transparent filter sidebar, have made the dashboard cleaner and more visually appealing.

## Dashboard limitations
- Reset button functionality: As mentioned earlier, the reset button isn't fully functional, which limits the ability to quickly clear filters and reset the data.


## Potential future improvements and additions
- Time-based visualizations: Adding the density chart or other time-series analysis tools would greatly benefit decision-makers by allowing them to track trends and patterns over time.

- Interactive map enhancements: It would be helpful to add zoom functionality to the map and provide more information on hover for precincts and boroughs, enabling more detailed exploration of the data.