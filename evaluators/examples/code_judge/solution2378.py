import sys

# 增加Python的递归深度限制以支持分治
sys.setrecursionlimit(50000 + 5)

def solve():
    """
    主函数，读取输入并启动分治算法。
    """
    try:
        # 使用快速I/O
        input = sys.stdin.readline
        n_str, m_str = input().split()
        N, M = int(n_str), int(m_str)
        
        points = [list(map(int, input().split())) for _ in range(N)]
        lenses = [list(map(int, input().split())) for _ in range(M)]
        
    except (IOError, ValueError):
        return

    # 全局答案数组
    ans = [0] * M

    # 存储预计算的区间最值
    max_a_left = [0] * N
    min_b_left = [0] * N
    max_a_right = [0] * N
    min_b_right = [0] * N

    def conquer(l, mid, r):
        # 1. 预计算左半部分从i到mid的最值
        max_a_left[mid] = points[mid][0]
        min_b_left[mid] = points[mid][1]
        for i in range(mid - 1, l - 1, -1):
            max_a_left[i] = max(points[i][0], max_a_left[i + 1])
            min_b_left[i] = min(points[i][1], min_b_left[i + 1])
            
        # 2. 预计算右半部分从mid+1到j的最值
        max_a_right[mid + 1] = points[mid + 1][0]
        min_b_right[mid + 1] = points[mid + 1][1]
        for j in range(mid + 2, r + 1):
            max_a_right[j] = max(points[j][0], max_a_right[j - 1])
            min_b_right[j] = min(points[j][1], min_b_right[j - 1])

        # 3. 为每个镜头找到最优的跨越区间
        for i in range(M):
            c, d = lenses[i]
            
            # --- 找最左的i ---
            # 二分找满足 max_a <= d 的最小 i
            low, high = l, mid
            i_a = -1
            while low <= high:
                m = (low + high) // 2
                if max_a_left[m] <= d:
                    i_a = m
                    high = m - 1
                else:
                    low = m + 1
            if i_a == -1: continue # 此镜头无法满足任何左半部分

            # 二分找满足 min_b >= c 的最小 i
            low, high = l, mid
            i_b = -1
            while low <= high:
                m = (low + high) // 2
                if min_b_left[m] >= c:
                    i_b = m
                    high = m - 1
                else:
                    low = m + 1
            if i_b == -1: continue

            min_i = max(i_a, i_b)

            # --- 找最右的j ---
            # 二分找满足 max_a <= d 的最大 j
            low, high = mid + 1, r
            j_a = -1
            while low <= high:
                m = (low + high) // 2
                if max_a_right[m] <= d:
                    j_a = m
                    low = m + 1
                else:
                    high = m - 1
            if j_a == -1: continue # 此镜头无法满足任何右半部分

            # 二分找满足 min_b >= c 的最大 j
            low, high = mid + 1, r
            j_b = -1
            while low <= high:
                m = (low + high) // 2
                if min_b_right[m] >= c:
                    j_b = m
                    low = m + 1
                else:
                    high = m - 1
            if j_b == -1: continue
            
            max_j = min(j_a, j_b)

            # --- 更新答案 ---
            if min_i <= mid and max_j > mid:
                ans[i] = max(ans[i], max_j - min_i + 1)


    # 分治主函数
    def divide(l, r):
        if l > r:
            return
        if l == r:
            for i in range(M):
                c, d = lenses[i]
                if points[l][0] <= d and c <= points[l][1]:
                    ans[i] = max(ans[i], 1)
            return

        mid = l + (r - l) // 2
        divide(l, mid)
        divide(mid + 1, r)
        conquer(l, mid, r)
        
    divide(0, N - 1)

    for val in ans:
        print(val)

if __name__ == "__main__":
    solve()