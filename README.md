# GlowTracker
**GlowTracker** is a price-tracking application designed for monitoring beauty products (skincare 🫧 and makeup 💄) across selected online stores. It helps users avoid overpaying by automatically checking product prices and notifying them about any changes. The app stores price history, tracks trends, and highlights the best time to buy a product.

## Key Features:
### Product Management:
- Add, edit, and remove products from your personal tracking list
- Store product name, brand, URL, description, and optional target price
- Organize products by brand or category

### Automatic Price Monitoring:
- Regularly checks product pages for price updates
- Customizable checking frequency (hourly, daily)
- Detects price increases and drops

### Alerts:
- Notifies the user when: a price drops, a target price is reached etc.

### Price History & Visualization:
- Stores historical price data
- Displays price changes over time using visual charts
- Allows users to analyze product price trends

### Filtering & Search:
- View all tracked products in one place
- Filter by: price drop, price increase, products below target price
- Search by name, brand, or category

### Statistics:
- Number of price drops in the last 7 days
- Average price change per product
- Products currently at their lowest recorded price

## Planned Interface

The application will include a graphical dashboard (Streamlit-based) where users can:
- manage tracked products
- visualize price history
- review statistics
- manually trigger price checks

### Supported stores:
- [Cosibella](https://cosibella.pl/)

## Architecture (TBD)

GlowTracker is designed as a modular application with a clear separation of different concerns. The core logic is isolated from both the UI and the web scraping layer, allowing each component to be developed, tested, and extended independently.

The application follows a simple data-pipeline approach: product pages are fetched, prices are extracted, stored in the database, and then analyzed to generate statistics and user notifications.

**Data Flow:** User -> PriceTracker (service layer) -> Scraper -> Parsed product price -> Database (SQLite) -> Statistics/Events -> Notifications/UI (Streamlit)

**Core service: PriceTracker**
PriceTracker is the central service layer of the application. It manages the entire monitoring process and contains the business logic of the system. 

It is responsible for:
- retrieving tracked products
- checking current product prices
- comparing them with previously recorded values
- storing price history
- detecting important events (price drop, price increase, target price reached)
- triggering notifications
- providing aggregated data for the UI dashboard

The UI (Streamlit dashboard) communicates only with this service layer and does not directly access the database or the scraper.

**PriceTracker** does not directly implement data storage, scraping, or notifications. Instead, these components are injected into the class during initialization.

**Injected dependencies:**
- database layer
- scraper
- notifier
- logger (to keep record of system activity and errors)

**Key modules**:
- tracker.py: service layer and monitoring logic
- database.py: data storage and database operations
- main.py: application entry point and initialization
- notifications.py: sending alerts about price changes
- scraper.py: fetching and parsing prices from online pages
- app.py: Streamlit dashboard (presentation layer)
  
## Run locally (TBD)

## Roadmap (TBD)