# Python 列表常用方法

| 方法 | 作用 | 样例 |
|------|------|------|
| `append(x)` | 在列表末尾添加元素 | `lst = [1, 2]; lst.append(3)` → `[1, 2, 3]` |
| `extend(iterable)` | 将可迭代对象中的元素逐个追加到列表末尾 | `lst = [1, 2]; lst.extend([3, 4])` → `[1, 2, 3, 4]` |
| `insert(i, x)` | 在指定索引位置插入元素 | `lst = [1, 3]; lst.insert(1, 2)` → `[1, 2, 3]` |
| `remove(x)` | 移除第一个匹配的元素，不存在则报错 | `lst = [1, 2, 2, 3]; lst.remove(2)` → `[1, 2, 3]` |
| `pop([i])` | 移除并返回指定索引的元素，默认最后一个 | `lst = [1, 2, 3]; lst.pop()` → `3`，列表变为 `[1, 2]` |
| `clear()` | 清空列表，移除所有元素 | `lst = [1, 2, 3]; lst.clear()` → `[]` |
| `index(x[, start[, end]])` | 返回第一个匹配元素的索引，可指定查找范围 | `lst = ['a', 'b', 'c', 'b']; lst.index('b')` → `1` |
| `count(x)` | 返回元素在列表中出现的次数 | `lst = [1, 2, 2, 3, 2]; lst.count(2)` → `3` |
| `sort(key=None, reverse=False)` | 原地排序，可指定排序键和是否降序 | `lst = [3, 1, 2]; lst.sort()` → `[1, 2, 3]` |
| `reverse()` | 原地反转列表顺序 | `lst = [1, 2, 3]; lst.reverse()` → `[3, 2, 1]` |
| `copy()` | 返回列表的浅拷贝 | `lst = [1, 2, 3]; lst2 = lst.copy()` |

## 说明

- **原地操作**：`append`、`extend`、`insert`、`remove`、`pop`、`clear`、`sort`、`reverse` 会直接修改原列表，无返回值（`pop` 除外，会返回被移除的元素）
- **非原地操作**：`index`、`count`、`copy` 不修改原列表，返回新值
