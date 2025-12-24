
class SpatialHash:
    """
    A spatial hash grid for efficient 2D collision detection and proximity queries.
    Instead of checking every object against every other object (O(N^2)), 
    we only check objects in the same grid cells (O(N) usually).
    """
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.contents = {}  # Map (x, y) -> set([objects])

    def _get_cell_coords(self, x, y):
        return int(x // self.cell_size), int(y // self.cell_size)

    def _get_cells_for_rect(self, rect):
        """Returns a list of cell coordinates that the rect overlaps with."""
        start_x, start_y = self._get_cell_coords(rect.left, rect.top)
        end_x, end_y = self._get_cell_coords(rect.right, rect.bottom)
        
        cells = []
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                cells.append((x, y))
        return cells

    def add(self, obj):
        """Add an object to the spatial hash."""
        if not hasattr(obj, 'rect'):
            return 
            
        cells = self._get_cells_for_rect(obj.rect)
        for cell in cells:
            if cell not in self.contents:
                self.contents[cell] = set()
            self.contents[cell].add(obj)
            
        # Store current cells on object for fast updates
        obj._spatial_hash_cells = cells

    def remove(self, obj):
        """Remove an object from the spatial hash."""
        if hasattr(obj, '_spatial_hash_cells'):
            for cell in obj._spatial_hash_cells:
                if cell in self.contents:
                    self.contents[cell].discard(obj)
                    if not self.contents[cell]:  # Clean up empty cells
                        del self.contents[cell]
            del obj._spatial_hash_cells

    def update(self, obj):
        """Update an object's position in the spatial hash."""
        self.remove(obj)
        self.add(obj)

    def get_nearby(self, rect):
        """
        Get all objects in the same cells as the given rect.
        Returns a set of objects.
        """
        cells = self._get_cells_for_rect(rect)
        nearby_objects = set()
        for cell in cells:
            if cell in self.contents:
                nearby_objects.update(self.contents[cell])
        return nearby_objects
