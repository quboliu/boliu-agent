# Before and after

**Question:** "Should I use `useMemo` for this filtered list?"

Before (108 words):
> Great question! Performance optimization is a crucial aspect of building robust React applications. `useMemo` is a powerful hook that allows you to memoize expensive computations. However, it's important to note that it's not always necessary to use it. There are several factors to consider, such as the size of your list, the complexity of your filter function, and how often your component re-renders. In general, it's a best practice to avoid premature optimization. That said, if you find that your component is experiencing performance issues, `useMemo` can be a great tool. In summary, whether you should use `useMemo` depends on your specific use case. I hope this helps!

After (54 words):
> Probably not. Filtering a few hundred items takes well under a millisecond, and `useMemo` has its own overhead. Add it if the React Profiler shows this render is slow, or if the filtered array goes to a memoized child or an effect's dependency list, where a new array on every render causes extra work.

The "before" names factors without saying how they decide anything. The "after" answers first, gives the two conditions that would change the answer, and names the mechanism behind the second (a new array reference on every render), so the reader can judge cases it doesn't list.

**PR description.**

Before:
> This PR introduces a comprehensive refactoring of the authentication module to leverage a more robust and scalable approach. The changes significantly improve performance and maintainability while ensuring seamless integration with existing systems.

After:
> Replace the per-request session lookup in Postgres with signed JWTs verified in middleware. This removes ~1,200 QPS from the primary database at peak (see the linked dashboard). Existing sessions stay valid until they expire; clients need no changes.
