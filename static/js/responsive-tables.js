/**
 * Responsive Tables Handler
 * Automatically converts tables to mobile-friendly formats
 */

class ResponsiveTables {
    constructor() {
        this.init();
    }

    init() {
        this.setupTables();
        this.handleWindowResize();
    }

    setupTables() {
        // Find all tables and make them responsive
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            this.makeTableResponsive(table);
        });
    }

    makeTableResponsive(table) {
        // Skip if already processed
        if (table.dataset.responsive === 'true') return;

        const container = table.closest('.table-container');
        if (!container) return;

        // Mark as processed
        table.dataset.responsive = 'true';

        // Create card-based alternative for mobile
        this.createCardAlternative(table, container);
        
        // Add horizontal scroll for desktop
        container.style.overflowX = 'auto';
        container.style.webkitOverflowScrolling = 'touch';
    }

    createCardAlternative(table, container) {
        // Extract headers
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => 
            th.textContent.trim()
        );

        if (headers.length === 0) return;

        // Create card container
        const cardContainer = document.createElement('div');
        cardContainer.className = 'table-responsive-cards';
        cardContainer.style.display = 'none'; // Hidden by default, shown via CSS media query

        // Process each row
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            const card = this.createCardFromRow(row, headers, index);
            cardContainer.appendChild(card);
        });

        // Insert card container after table
        container.appendChild(cardContainer);
    }

    createCardFromRow(row, headers, index) {
        const card = document.createElement('div');
        card.className = 'responsive-card';

        // Add card header if first cell looks like a title
        const firstCell = row.cells[0];
        if (firstCell) {
            const cardHeader = document.createElement('div');
            cardHeader.className = 'responsive-card-header';
            cardHeader.textContent = firstCell.textContent.trim();
            card.appendChild(cardHeader);
        }

        // Add rows for each data cell (skip first one used as header)
        for (let i = 1; i < row.cells.length && i < headers.length; i++) {
            const cell = row.cells[i];
            const header = headers[i];

            const cardRow = document.createElement('div');
            cardRow.className = 'responsive-card-row';

            const label = document.createElement('div');
            label.className = 'responsive-card-label';
            label.textContent = header;

            const value = document.createElement('div');
            value.className = 'responsive-card-value';
            value.innerHTML = cell.innerHTML; // Preserve HTML content like badges, buttons

            cardRow.appendChild(label);
            cardRow.appendChild(value);
            card.appendChild(cardRow);
        }

        // Add actions if last cell contains buttons
        const lastCell = row.cells[row.cells.length - 1];
        if (lastCell && (lastCell.querySelector('.btn') || lastCell.querySelector('button'))) {
            const actionsRow = document.createElement('div');
            actionsRow.className = 'responsive-card-row responsive-card-actions';
            actionsRow.innerHTML = lastCell.innerHTML;
            card.appendChild(actionsRow);
        }

        return card;
    }

    handleWindowResize() {
        window.addEventListener('resize', () => {
            this.updateTableVisibility();
        });

        // Initial check
        this.updateTableVisibility();
    }

    updateTableVisibility() {
        const isMobile = window.innerWidth <= 768;
        const containers = document.querySelectorAll('.table-container');

        containers.forEach(container => {
            const table = container.querySelector('table[data-responsive="true"]');
            const cards = container.querySelector('.table-responsive-cards');

            if (table && cards) {
                // Let CSS handle visibility, but ensure elements exist
                container.classList.toggle('mobile-view', isMobile);
            }
        });
    }

    // Method to refresh tables (useful for dynamically loaded content)
    refresh() {
        // Clear processed flags
        document.querySelectorAll('table[data-responsive="true"]').forEach(table => {
            delete table.dataset.responsive;
        });

        // Remove existing card alternatives
        document.querySelectorAll('.table-responsive-cards').forEach(cards => {
            cards.remove();
        });

        // Reinitialize
        this.setupTables();
    }

    // Method to enable card view for specific table
    enableCardsFor(tableSelector) {
        const table = document.querySelector(tableSelector);
        if (table) {
            const container = table.closest('.table-container');
            if (container) {
                container.classList.add('use-cards');
            }
        }
    }

    // Method to handle sortable tables
    makeSortable(tableSelector) {
        const table = document.querySelector(tableSelector);
        if (!table) return;

        const headers = table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            if (header.dataset.sortable === 'false') return;

            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort sort-icon"></i>';
            
            header.addEventListener('click', () => {
                this.sortTable(table, index);
            });
        });
    }

    sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Determine sort direction
        const header = table.querySelectorAll('thead th')[columnIndex];
        const isAscending = !header.classList.contains('sort-asc');
        
        // Clear all sort classes
        table.querySelectorAll('thead th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            const icon = th.querySelector('.sort-icon');
            if (icon) icon.className = 'fas fa-sort sort-icon';
        });

        // Add sort class to current header
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        const icon = header.querySelector('.sort-icon');
        if (icon) {
            icon.className = `fas fa-sort-${isAscending ? 'up' : 'down'} sort-icon`;
        }

        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try to parse as numbers
            const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // String comparison
            return isAscending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        });

        // Reorder rows in DOM
        rows.forEach(row => tbody.appendChild(row));

        // Refresh card alternatives
        this.refreshCardsForTable(table);
    }

    refreshCardsForTable(table) {
        const container = table.closest('.table-container');
        if (!container) return;

        // Remove existing cards
        const existingCards = container.querySelector('.table-responsive-cards');
        if (existingCards) {
            existingCards.remove();
        }

        // Recreate cards with new order
        this.createCardAlternative(table, container);
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.responsiveTables = new ResponsiveTables();
    console.log('📱 Responsive tables initialized');
});

// Export for manual use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResponsiveTables;
}