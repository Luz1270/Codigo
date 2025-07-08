#include <iostream>
#include <queue>
#include <vector>
#include <algorithm>  // Para std::reverse
#include <windows.h>  // Para Sleep() y system("cls")

const int ROWS = 8;
const int COLS = 8;

int maze[ROWS][COLS] = {
    {1,1,1,1,1,1,1,1},
    {1,0,0,0,1,0,0,1},
    {1,0,1,0,0,0,1,1},
    {1,0,1,1,1,0,1,1},
    {1,0,0,0,1,0,0,1},
    {1,1,1,0,1,1,0,1},
    {1,0,0,0,0,0,0,1},
    {1,1,1,1,1,1,1,1}
};

struct Pos {
    int x, y;
};

bool visited[ROWS][COLS] = { false };
Pos prev[ROWS][COLS];

std::vector<Pos> bfs(Pos start, Pos end) {
    std::queue<Pos> q;
    q.push(start);
    visited[start.y][start.x] = true;

    int dx[] = {-1,1,0,0};
    int dy[] = {0,0,-1,1};

    while (!q.empty()) {
        Pos cur = q.front(); q.pop();
        if (cur.x == end.x && cur.y == end.y)
            break;

        for (int i = 0; i < 4; ++i) {
            int nx = cur.x + dx[i];
            int ny = cur.y + dy[i];
            if (nx >= 0 && ny >= 0 && nx < COLS && ny < ROWS &&
                maze[ny][nx] == 0 && !visited[ny][nx]) {
                visited[ny][nx] = true;
                prev[ny][nx] = cur;
                q.push({nx, ny});
            }
        }
    }

    std::vector<Pos> path;
    for (Pos at = end; !(at.x == start.x && at.y == start.y); at = prev[at.y][at.x])
        path.push_back(at);
    path.push_back(start);
    std::reverse(path.begin(), path.end());
    return path;
}

void printMaze(Pos player) {
    system("cls"); // Limpiar la pantalla (Windows)
    for (int y = 0; y < ROWS; y++) {
        for (int x = 0; x < COLS; x++) {
            if (player.x == x && player.y == y)
                std::cout << "P ";
            else if (maze[y][x] == 1)
                std::cout << "# ";
            else
                std::cout << ". ";
        }
        std::cout << "\n";
    }
}

int main() {
    Pos start = {1, 1};
    Pos end = {6, 6};
    std::vector<Pos> path = bfs(start, end);

    for (const auto& pos : path) {
        printMaze(pos);
        Sleep(300); // milisegundos
    }

    std::cout << "¡Llegaste a la meta!\n";
    return 0;
}
