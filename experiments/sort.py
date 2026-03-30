class Solution:

    nums = [3,4,5,1,2]
    def findMin(self, nums: list[int]) -> int:
        """ Find minimum value among the list values
        :param nums: list of values
        """
        left = 0
        right = len(nums) - 1
        while left < right:
            mid = left + (right - left) // 2
            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid
        return nums[left]

s = Solution()
print(s.findMin([3, 4, 5, 1, 2]))  # Expected: 1
