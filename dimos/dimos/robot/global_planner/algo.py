import math
import heapq
from typing import Optional, Tuple
from collections import deque
from dimos.types.path import Path
from dimos.types.vector import VectorLike, Vector
from dimos.types.costmap import Costmap


def find_nearest_free_cell(
    costmap: Costmap, 
    position: VectorLike, 
    cost_threshold: int = 90,
    max_search_radius: int = 20
) -> Tuple[int, int]:
    """
    Find the nearest unoccupied cell in the costmap using BFS.
    
    Args:
        costmap: Costmap object containing the environment
        position: Position to find nearest free cell from
        cost_threshold: Cost threshold above which a cell is considered an obstacle
        max_search_radius: Maximum search radius in cells
        
    Returns:
        Tuple of (x, y) in grid coordinates of the nearest free cell,
        or the original position if no free cell is found within max_search_radius
    """
    # Convert world coordinates to grid coordinates
    grid_pos = costmap.world_to_grid(position)
    start_x, start_y = int(grid_pos.x), int(grid_pos.y)
    
    # If the cell is already free, return it
    if 0 <= start_x < costmap.width and 0 <= start_y < costmap.height:
        if costmap.grid[start_y, start_x] < cost_threshold:
            return (start_x, start_y)
    
    # BFS to find nearest free cell
    queue = deque([(start_x, start_y, 0)])  # (x, y, distance)
    visited = set([(start_x, start_y)])
    
    # Possible movements (8-connected grid)
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),  # horizontal/vertical
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # diagonal
    ]
    
    while queue:
        x, y, dist = queue.popleft()
        
        # Check if we've reached the maximum search radius
        if dist > max_search_radius:
            print(f"Could not find free cell within {max_search_radius} cells of ({start_x}, {start_y})")
            return (start_x, start_y)  # Return original position if no free cell found
        
        # Check if this cell is valid and free
        if 0 <= x < costmap.width and 0 <= y < costmap.height:
            if costmap.grid[y, x] < cost_threshold:
                print(f"Found free cell at ({x}, {y}), {dist} cells away from ({start_x}, {start_y})")
                return (x, y)
        
        # Add neighbors to the queue
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))
    
    # If the queue is empty and no free cell is found, return the original position
    return (start_x, start_y)


def astar(
    costmap: Costmap,
    goal: VectorLike,
    start: VectorLike = (0.0, 0.0),
    cost_threshold: int = 90,
    allow_diagonal: bool = True,
) -> Optional[Path]:
    """
    A* path planning algorithm from start to goal position.

    Args:
        costmap: Costmap object containing the environment
        goal: Goal position as any vector-like object
        start: Start position as any vector-like object (default: origin [0,0])
        cost_threshold: Cost threshold above which a cell is considered an obstacle
        allow_diagonal: Whether to allow diagonal movements

    Returns:
        Path object containing waypoints, or None if no path found
    """
    # Convert world coordinates to grid coordinates directly using vector-like inputs
    start_vector = costmap.world_to_grid(start)
    goal_vector = costmap.world_to_grid(goal)
    
    # Store original positions for reference
    original_start = (int(start_vector.x), int(start_vector.y))
    original_goal = (int(goal_vector.x), int(goal_vector.y))
    
    adjusted_start = original_start
    adjusted_goal = original_goal

    # Check if start is out of bounds or in an obstacle
    start_valid = (0 <= start_vector.x < costmap.width and 
                  0 <= start_vector.y < costmap.height)
    
    start_in_obstacle = False
    if start_valid:
        start_in_obstacle = costmap.grid[int(start_vector.y), int(start_vector.x)] >= cost_threshold
    
    if not start_valid or start_in_obstacle:
        print("Start position is out of bounds or in an obstacle, finding nearest free cell")
        adjusted_start = find_nearest_free_cell(costmap, start, cost_threshold)
        # Update start_vector for later use
        start_vector = Vector(adjusted_start[0], adjusted_start[1])

    # Check if goal is out of bounds or in an obstacle
    goal_valid = (0 <= goal_vector.x < costmap.width and 
                 0 <= goal_vector.y < costmap.height)
    
    goal_in_obstacle = False
    if goal_valid:
        goal_in_obstacle = costmap.grid[int(goal_vector.y), int(goal_vector.x)] >= cost_threshold
    
    if not goal_valid or goal_in_obstacle:
        print("Goal position is out of bounds or in an obstacle, finding nearest free cell")
        adjusted_goal = find_nearest_free_cell(costmap, goal, cost_threshold)
        # Update goal_vector for later use
        goal_vector = Vector(adjusted_goal[0], adjusted_goal[1])

    # Define possible movements (8-connected grid)
    if allow_diagonal:
        # 8-connected grid: horizontal, vertical, and diagonal movements
        directions = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
    else:
        # 4-connected grid: only horizontal and vertical ts
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Cost for each movement (straight vs diagonal)
    sc = 1.0
    dc = 1.42
    movement_costs = [sc, sc, sc, sc, dc, dc, dc, dc] if allow_diagonal else [sc, sc, sc, sc]

    # A* algorithm implementation
    open_set = []  # Priority queue for nodes to explore
    closed_set = set()  # Set of explored nodes

    # Use adjusted positions as tuples for dictionary keys
    start_tuple = adjusted_start
    goal_tuple = adjusted_goal

    # Dictionary to store cost from start and parents for each node
    g_score = {start_tuple: 0}
    parents = {}

    # Heuristic function (Euclidean distance)
    def heuristic(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # Start with the starting node
    f_score = g_score[start_tuple] + heuristic(start_tuple[0], start_tuple[1], goal_tuple[0], goal_tuple[1])
    heapq.heappush(open_set, (f_score, start_tuple))

    while open_set:
        # Get the node with the lowest f_score
        _, current = heapq.heappop(open_set)
        current_x, current_y = current

        # Check if we've reached the goal
        if current == goal_tuple:
            # Reconstruct the path
            waypoints = []
            while current in parents:
                world_point = costmap.grid_to_world(current)
                waypoints.append(world_point)
                current = parents[current]

            # Add the start position
            start_world_point = costmap.grid_to_world(start_tuple)
            waypoints.append(start_world_point)

            # Reverse the path (start to goal)
            waypoints.reverse()

            # Add the goal position if it's not already included
            goal_point = costmap.grid_to_world(goal_tuple)

            if not waypoints or waypoints[-1].distance(goal_point) > 1e-5:
                waypoints.append(goal_point)
                
            # If we adjusted the goal, add the original goal as the final point
            if adjusted_goal != original_goal and goal_valid:
                original_goal_point = costmap.grid_to_world(original_goal)
                waypoints.append(original_goal_point)

            return Path(waypoints)

        # Add current node to closed set
        closed_set.add(current)

        # Explore neighbors
        for i, (dx, dy) in enumerate(directions):
            neighbor_x, neighbor_y = current_x + dx, current_y + dy
            neighbor = (neighbor_x, neighbor_y)

            # Check if the neighbor is valid
            if not (0 <= neighbor_x < costmap.width and 0 <= neighbor_y < costmap.height):
                continue

            # Check if the neighbor is already explored
            if neighbor in closed_set:
                continue

            # Check if the neighbor is an obstacle
            neighbor_val = costmap.grid[neighbor_y, neighbor_x]
            if neighbor_val >= cost_threshold:  # or neighbor_val < 0:
                continue

            obstacle_proximity_penalty = costmap.grid[neighbor_y, neighbor_x] / 25
            tentative_g_score = g_score[current] + movement_costs[i] + (obstacle_proximity_penalty * movement_costs[i])

            # Get the current g_score for the neighbor or set to infinity if not yet explored
            neighbor_g_score = g_score.get(neighbor, float("inf"))

            # If this path to the neighbor is better than any previous one
            if tentative_g_score < neighbor_g_score:
                # Update the neighbor's scores and parent
                parents[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor_x, neighbor_y, goal_tuple[0], goal_tuple[1])

                # Add the neighbor to the open set with its f_score
                heapq.heappush(open_set, (f_score, neighbor))

    # If we get here, no path was found
    return None
