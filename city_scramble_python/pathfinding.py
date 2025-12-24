import heapq
import pygame
from settings import MAP_WIDTH, MAP_HEIGHT, ENEMY_SIZE

class PathfindingGrid:
    """Grid-based pathfinding for AI navigation"""
    
    def __init__(self, width, height, obstacles, cell_size=40):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        self.grid = []
        self.build_grid(obstacles)
    
    def build_grid(self, obstacles):
        """Create navigation grid where 0 = walkable, 1 = blocked"""
        # Initialize empty grid
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Mark cells occupied by obstacles as blocked
        for obstacle in obstacles:
            # Get grid coordinates for obstacle bounds
            x1 = max(0, obstacle.rect.left // self.cell_size)
            y1 = max(0, obstacle.rect.top // self.cell_size)
            x2 = min(self.grid_width - 1, obstacle.rect.right // self.cell_size)
            y2 = min(self.grid_height - 1, obstacle.rect.bottom // self.cell_size)
            
            # Mark all cells within obstacle as blocked
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    if 0 <= y < self.grid_height and 0 <= x < self.grid_width:
                        self.grid[y][x] = 1
    
    def rebuild(self, obstacles):
        """Rebuild grid when obstacles change"""
        self.build_grid(obstacles)
    
    def world_to_grid(self, x, y):
        """Convert world coordinates to grid coordinates"""
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        # Clamp to grid bounds
        grid_x = max(0, min(self.grid_width - 1, grid_x))
        grid_y = max(0, min(self.grid_height - 1, grid_y))
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_x, grid_y):
        """Convert grid coordinates to world coordinates (center of cell)"""
        x = grid_x * self.cell_size + self.cell_size // 2
        y = grid_y * self.cell_size + self.cell_size // 2
        return (x, y)
    
    def is_walkable(self, grid_x, grid_y):
        """Check if grid cell is walkable"""
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return False
        return self.grid[grid_y][grid_x] == 0
    
    def get_neighbors(self, grid_x, grid_y):
        """Get walkable neighbors (8 directions including diagonals)"""
        neighbors = []
        # 8 directions: N, NE, E, SE, S, SW, W, NW
        directions = [
            (0, -1), (1, -1), (1, 0), (1, 1),
            (0, 1), (-1, 1), (-1, 0), (-1, -1)
        ]
        
        for dx, dy in directions:
            nx, ny = grid_x + dx, grid_y + dy
            if self.is_walkable(nx, ny):
                # For diagonal moves, check if adjacent cells are also walkable
                # to prevent cutting corners through walls
                if dx != 0 and dy != 0:
                    if not self.is_walkable(grid_x + dx, grid_y) or \
                       not self.is_walkable(grid_x, grid_y + dy):
                        continue
                neighbors.append((nx, ny))
        
        return neighbors


def heuristic(a, b):
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def find_path(start_pos, goal_pos, pathfinding_grid):
    """
    A* pathfinding algorithm
    
    Args:
        start_pos: (x, y) world coordinates
        goal_pos: (x, y) world coordinates
        pathfinding_grid: PathfindingGrid instance
    
    Returns:
        List of (x, y) world coordinate waypoints, or empty list if no path found
    """
    # Convert world coordinates to grid coordinates
    start = pathfinding_grid.world_to_grid(start_pos[0], start_pos[1])
    goal = pathfinding_grid.world_to_grid(goal_pos[0], goal_pos[1])
    
    # If start or goal is not walkable, return empty path
    if not pathfinding_grid.is_walkable(start[0], start[1]) or \
       not pathfinding_grid.is_walkable(goal[0], goal[1]):
        return []
    
    # If already at goal, return empty path
    if start == goal:
        return []
    
    # A* algorithm
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                # Convert grid coordinates back to world coordinates
                world_pos = pathfinding_grid.grid_to_world(current[0], current[1])
                path.append(world_pos)
                current = came_from[current]
            path.reverse()
            return path
        
        for neighbor in pathfinding_grid.get_neighbors(current[0], current[1]):
            # Calculate tentative g_score
            # Diagonal moves cost more (1.4) than straight moves (1.0)
            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])
            move_cost = 1.4 if (dx + dy == 2) else 1.0
            
            tentative_g_score = g_score[current] + move_cost
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # No path found
    return []
