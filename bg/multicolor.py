# -*- coding: utf-8 -*-
from collections import Counter
from copy import deepcopy

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"


class Multicolor(object):
    """ Class providing implementation of multi-color notion for edges in :class:`bg.breakpoint_graph.BreakpointGraph`.

    Multi-color is a specific property of edges in Breakpoint Graph combinatorial object which represents similar adjacencies between genomic material in multiple genomes.

    This class supports the following attributes, that carry information colors and their multiplicity of edges in :class:`bg.breakpoint_graph.BreakpointGraph`.

    *    :attr:`Multicolor.multicolors`: a python Counter object which contains information about colors and their multiplicity for a given :class:`Multicolor` instance
    *    :attr:`Multicolor.colors`: a property attribute providing a set of colors in :attr:`Multicolor.multicolors` attribute, hiding information about colors multiplicity

    Main operations:

    *   ``+``, ``-``, ``+=``, ``-=``, ``==``, ``>``, ``>=``, ``<``, ``<=``
    *    :meth:`Multicolor.update`: updates information in :attr:`Multicolor.multicolors` attribute of respective instance
    *    :meth:`Multicolor.merge`: creates a new :class:`Multicolor` object out of a list of provided :class:`Multicolor` objects, gathering respective information about colors and their multiplicity
    *    :meth:`Multicolor.left_merge`: updates respective :class:`Multicolor` instance with information from supplied :class:`Multicolor` object
    *    :meth:`Multicolor.delete`: reduces information in respective instance :attr:`Multicolor.multicolors` attribute by iterating over supplied data
    *    :meth:`Multicolor.similarity_score` computes how similar two supplied :class:`Multicolor` object are
    *    :meth:`Multicolor.split_colors` produces several new instances of :class:`Multicolor` object by splitting information about colors by using provided guidance iterable set-like object
    """

    def __init__(self, *args):
        """ Initialization of :class:`Multicolor` object.

        Initialization is performed by supplied variable number of colors, that respective :class:`Multicolor` object must contain information about Multiplicity of each color is determined by the number of times it occurs as argument in initialization process.

        :param args: variable number of colors to contain information about
        :type args: any hashable python object
        :return: a new instance of :class:`Multicolor`
        :rtype: :class:`Multicolor`
        """
        self.multicolors = Counter(arg for arg in args)

    def update(self, *args):
        """ Updates information about colors and their multiplicity in respective :class:`Multicolor` instance.

        By iterating over supplied arguments each of which should represent a color object, updates information about colors and their multiplicity in current :class:`Multicolor` instance.

        :param args: variable number of colors to add to currently existing multi colors data
        :type args: any hashable python object
        :return: ``None``, performs inplace changes to :attr:`Multicolor.multicolors` attribute
        """
        self.multicolors = self.multicolors + Counter(arg for arg in args)

    @classmethod
    def left_merge(cls, multicolor1, multicolor2):
        """ Updates first supplied :class:`Multicolor` instance with information from second supplied :class:`Multicolor` instance.

        Works as proxy to respective call to private static method :meth:`Multicolor._Multicolor__left_merge` for purposes of inheritance compatibility.

        Accounts for subclassing.

        :param multicolor1: instance to update information in
        :type multicolor1: :class:`Multicolor`
        :param multicolor2: instance to use information for update from
        :type multicolor2: :class:`Multicolor`
        :return: updated first supplied :class:`Multicolor` instance
        :rtype: :class:`Multicolor`
        """
        return cls.__left_merge(multicolor1, multicolor2)

    @classmethod
    def merge(cls, *multicolors):
        """ Produces a new :class:`Multicolor` object resulting from gathering information from all supplied :class:`Multicolor` instances.

        Works as proxy to respective call to private static method :meth:`Multicolor._Multicolor__merge` for purposes of inheritance compatibility.

        :param multicolors: variable number of :class:`Multicolor` objects
        :type multicolors: :class:`Multicolor`
        :return: object containing gathered information from all supplied arguments
        :rtype: :class:`Multicolor`
        """
        return cls.__merge(*multicolors)

    def delete(self, multicolor):
        """ Reduces information :class:`Multicolor` attribute by iterating over supplied colors data.

        Works as proxy to respective call to private static method :meth:`Multicolor._Multicolor__delete` for purposes of inheritance compatibility.

        :param multicolor: information about colors to be deleted from :class:`Multicolor` object
        :type multicolor: any iterable with colors object as entries or :class:`Multicolor`
        :return: ``None``, performs inplace changes
        """
        self.__delete(multicolor)

    def __delete(self, multicolor):
        """ Reduces information :class:`Multicolor` attribute by iterating over supplied colors data.

        In case supplied argument is a :class:`Multicolor` instance, multi-color specific information to de deleted is set to its :attr:`Multicolor.multicolors`.
        In other cases multi-color specific information to de deleted is obtained from iterating over the argument.

        Colors and their multiplicity is reduces with a help of ``-`` method of python Counter object.

        :param multicolor: information about colors to be deleted from :class:`Multicolor` object
        :type multicolor: any iterable with colors object as entries or :class:`Multicolor`
        :return: ``None``, performs inplace changes
        """
        if isinstance(multicolor, Multicolor):
            to_delete = multicolor.multicolors
        else:
            to_delete = Counter(color for color in multicolor)
        self.multicolors = self.multicolors - to_delete

    @classmethod
    def __merge(cls, *multicolors):
        """ Produces a new :class:`Multicolor` object resulting from gathering information from all supplied :class:`Multicolor` instances.

        New :class:`Multicolor` is created and its :attr:`Multicolor.multicolors` attribute is updated with similar attributes of supplied :class:`Multicolor` objects.

        Accounts for subclassing.

        :param multicolors: variable number of :class:`Multicolor` objects
        :type multicolors: :class:`Multicolor`
        :return: object containing gathered information from all supplied arguments
        :rtype: :class:`Multicolor`
        """
        result = cls()
        for multicolor in multicolors:
            result.multicolors = result.multicolors + multicolor.multicolors
        return result

    @staticmethod
    def __left_merge(multicolor1, multicolor2):
        """ Updates first supplied :class:`Multicolor` instance with information from second supplied :class:`Multicolor` instance.

        First supplied instances attribute :attr:`Multicolor.multicolors` is updated with a help of ``+`` method of python Counter object.

        :param multicolor1: instance to update information in
        :type multicolor1: :class:`Multicolor`
        :param multicolor2: instance to use information for update from
        :type multicolor2: :class:`Multicolor`
        :return: updated first supplied :class:`Multicolor` instance
        :rtype: :class:`Multicolor`
        """
        multicolor1.multicolors = multicolor1.multicolors + multicolor2.multicolors
        return multicolor1

    @staticmethod
    def similarity_score(multicolor1, multicolor2):
        """ Computes how similar two :class:`Multicolor` objects are from perspective of information, that they contain.

        Two multicolors are called to be similar if they contain same colors (at least one). Multiplicity of colors is taken into account as well.

        :param multicolor1: first out of two multi-colors to compute similarity between
        :type multicolor1: :class:`Multicolor`
        :param multicolor2: second out of two multi-colors to compute similarity between
        :type multicolor2: :class:`Multicolor`
        :return: the similarity score between two supplied :class:`Multicolor` object
        :rtype: ``int``
        """
        result = 0
        for key, value in multicolor1.multicolors.items():
            if key in multicolor2.multicolors:
                result += min(value, multicolor2.multicolors[key])
        return result

    @classmethod
    def split_colors(cls, multicolor, guidance=None, sorted_guidance=False,
                     account_for_color_multiplicity_in_guidance=True):
        """ Produces several new instances of :class:`Multicolor` object by splitting information about colors by using provided guidance iterable set-like object.

        Guidance is an iterable type of object where each entry has information about groups of colors that has to be separated for current :attr:`Multicolor.multicolors` chunk.
        If no Guidance is provided, single-color guidance of :attr:`Multicolor.multicolors` is created.
        Guidance object is first reversed sorted to iterate over it from larges color set to the smallest one, as small color sets might be subsets of bigger ones, and shall be utilized only if bigger sets didn't help in separating.

        During the first iteration over the guidance information all subsets of :attr:`Multicolor.multicolors` that equal to entries of guidance are recorded.
        During second iteration over remaining of the guidance information, if colors in :attr:`Multicolor.multicolors` form subsets of guidance entries, such instances are recorded.
        After this two iterations, the rest of :attr:`Multicolor.multicolors` is recorded as non-tackled and is recorded on its own.

        Multiplicity of all separated colors in respective chunks is preserved.

        Accounts for subclassing.

        :param multicolor: an instance information about colors in which is to be split
        :type multicolor: :class:`Multicolor`
        :param guidance: information how colors have to be split in current :class:`Multicolor` object
        :type guidance: iterable where each entry is iterable with colors entries
        :param sorted_guidance: a flag, that indicates is sorting of provided guidance is in order
        :return: a list of new :class:`Multicolor` object colors information in which complies with guidance information
        :rtype: ``list`` of :class:`Multicolor` objects
        """
        if guidance is None:
            ###############################################################################################
            #
            # if guidance is not specified, it will be derived from colors in the targeted multicolor
            # initially the multiplicity of colors remains as is
            #
            ###############################################################################################
            guidance = [Multicolor(*(color for _ in range(multicolor.multicolors[color]))) for color in multicolor.colors]
            ###############################################################################################
            #
            # since at this we have a single-colored (maybe with multiplicity greater than 1)
            # we don't need to sort anything, as there will be no overlapping multicolor in guidance
            #
            ###############################################################################################
            sorted_guidance = True
        ###############################################################################################
        #
        # a reference to the targeted multicolor.
        # such reference is created only for the future requirement to access information about original multicolor
        # Is done for the sake of code clarity and consistency.
        #
        ###############################################################################################
        splitting_multicolor = deepcopy(multicolor)
        if not account_for_color_multiplicity_in_guidance:
            ###############################################################################################
            #
            # we need to create a new guidance (even if original is perfect)
            # a new one shall preserve the order of the original, but all multicolors in it
            #   while keeping information about the actual colors itself, shall have multiplicity equal to 1
            #
            ###############################################################################################
            splitting_multicolor = Multicolor(*multicolor.colors)
            colors_guidance = [Multicolor(*tmp_multicolor.colors) for tmp_multicolor in guidance]
            ###############################################################################################
            #
            # since there might be different multicolors, with the same colors content
            # and they will be changed to same multicolors object, after colors multiplicity adjustment
            # we need, while preserving the order, leave only unique ones in (the first appearance)
            #
            ###############################################################################################
            unique = set()
            guidance = []
            for c_multicolor in colors_guidance:
                if c_multicolor.hashable_representation not in unique:
                    unique.add(c_multicolor.hashable_representation)
                    guidance.append(c_multicolor)
        if not sorted_guidance:
            ###############################################################################################
            #
            # if arguments in function call do not specify explicitly, that the guidance shall be used "as is"
            # it is sorted to put "bigger" multicolors in front, and smaller at the back
            # as bigger multicolor might contain several smaller multicolors from the guidance, but the correct splitting
            # always assumes that the smaller is the splitted result, the better it is
            # and such minimization can be obtained only if the biggest chunk of targeted multicolor are ripped off of it first
            #
            ###############################################################################################
            guidance = sorted({g_multicolor.hashable_representation for g_multicolor in guidance},
                              key=lambda g_multicolor: len(g_multicolor),
                              reverse=True)
            guidance = [Multicolor(*hashed) for hashed in guidance]
        first_run_result = []
        second_run_result = []
        for g_multicolor in guidance:
            ###############################################################################################
            #
            # first we determine which multicolors in guidance are fully present in the multicolor to split
            #   "<=" operator can be read as "is_multi_subset_of"
            # and retrieve as many copies of it from the multicolor, as we can
            # Example:
            #   multicolor has only one color "blue" with multiplicity "4"
            #   in guidance we have multicolor with color "blue" with multiplicity "2"
            #   we must retrieve it fully twice
            #
            ###############################################################################################
            ###############################################################################################
            #
            # empty guidance multicolors shall be ignored, as they have no impact on the splitting algorithm
            #
            ###############################################################################################
            if len(g_multicolor.colors) == 0:
                continue
            while g_multicolor <= splitting_multicolor:
                first_run_result.append(g_multicolor)
                splitting_multicolor -= g_multicolor
        for g_multicolor in guidance:
            ###############################################################################################
            #
            # secondly we determine which multicolors in guidance are partially present in the multicolor
            # NOTE that this is not possible for the case of tree consistent multicolor
            #   as every partially present
            #
            ###############################################################################################
            while len(g_multicolor.intersect(splitting_multicolor).multicolors) > 0:
                second_run_result.append(g_multicolor.intersect(splitting_multicolor))
                splitting_multicolor -= g_multicolor.intersect(splitting_multicolor)
        appendix = splitting_multicolor
        result = deepcopy(first_run_result) + deepcopy(second_run_result) + deepcopy([appendix] if len(appendix.multicolors) > 0 else [])
        if not account_for_color_multiplicity_in_guidance:
            ###############################################################################################
            #
            # if we didn't care for guidance multicolors colors multiplicity, we we splitting a specially created Multicolor
            # based only on the colors content.
            # After this is done, we need to restore the original multiplicity of each color in result multicolors to the
            # count they had in the targeted for splitting multicolor.
            # This is possible since in the case when we do not account for colors multiplicity in guidance, we have
            # splitting_color variable referencing not the supplied multicolor, and thus internal changes are not made to
            # supplied multicolor.
            #
            ###############################################################################################
            for r_multicolor in result:
                for color in r_multicolor.colors:
                    r_multicolor.multicolors[color] = multicolor.multicolors[color]
        return result

    def __sub__(self, other):
        """ Implementation of ``-`` operation for :class:`Multicolor`

        Creates a new :class:`Multicolor` instance by cloning current :class:`Multicolor` object and updating its :attr:`Multicolor.multicolors` attribute information by deleting multi-colors in supplied :class:`Multicolor` object.

        :param other: object, whose multi-color information to subtract form current one
        :type other: :class:`Multicolor`
        :return: new :class:`Multicolor` object, colors in which and their multiplicity result from subtracting of current :attr:`Multicolor.multicolors` and supplied :class:`Multicolor.multicolors` attributes.
        :rtype: :class:`Multicolor`
        :raises: ``TypeError``, if not :class:`Multicolor` instance is supplied
        """
        if not isinstance(other, Multicolor):
            raise TypeError
        result = Multicolor(*(color for color in self.multicolors.elements()))
        result.__delete(other)
        return result

    def __isub__(self, other):
        """ Implementation of ``-`` operation for :class:`Multicolor`

        Updates current :class:`Multicolor` instance by updating its :attr:`Multicolor.multicolors` attribute information by deleting multi-colors in supplied :attr:`Multicolor.multicolors` attribute.
        Utilizes ``-`` method of python Counter

        :param other: object, whose multi-color information to subtract form current one
        :type other: :class:`Multicolor`
        :return: updated current :class:`Multicolor` object
        :rtype: :class:`Multicolor`
        :raises: ``TypeError``, if not :class:`Multicolor` instance is supplied
        """
        if not isinstance(other, Multicolor):
            raise TypeError
        self.multicolors = self.multicolors - other.multicolors
        return self

    def __add__(self, other):
        """ Implementation of ``+`` operation for :class:`Multicolor`

        Invokes a private :meth:`Multicolor._Multicolor__merge` method to implement addition of two :class:`Multicolor` instances.

        :param other: object, whose multi-color information has to be added to current one
        :type other: :class:`Multicolor`
        :return: new :class:`Multicolor` object, colors in which and their multiplicity result from addition of current :attr:`Multicolor.multicolors` and supplied :attr:`Multicolor.multicolors`
        :rtype: :class:`Multicolor`
        :raises: ``TypeError``, if not :class:`Multicolor` instance is provided
        """
        if not isinstance(other, Multicolor):
            raise TypeError
        return Multicolor.__merge(self, other)

    def __iadd__(self, other):
        """ Implementation of ``+=`` operation for :class:`Multicolor`

        Invokes a private :meth:`Multicolor._Multicolor__merge` method to implement addition of two :class:`Multicolor` instances.

        :param other: object, whose multi-color information has to be added to current one
        :type other: :class:`Multicolor`
        :return: new :class:`Multicolor` object, colors in which and their multiplicity result from addition of current :attr:`Multicolor.multicolors` and supplied :attr:`Multicolor.multicolors`
        :rtype: :class:`Multicolor`
        :raises: ``TypeError``, if not :class:`Multicolor` instance is provided
        """
        if not isinstance(other, Multicolor):
            raise TypeError
        return Multicolor.__left_merge(self, other)

    def __eq__(self, other):
        """ Implementation of ``==`` operation for :class:`Multicolor`

        Two :class:`Multicolor` objects are called to be equal if colors that both of them contain and respective colors multiplicity are equal.
        :class:`Multicolor` instance never equals to non-:class:`Multicolor` object.
        Performs :attr:`Multicolor.multicolors` comparison with a help of ``==`` method of python Counter object.

        :param other: an object to compare to
        :type other: any python object
        :return: a flag of equality between current :class:`Multicolor` instance and supplied object
        :rtype: ``Boolean``
        """
        if not isinstance(other, Multicolor):
            return False
        return self.multicolors == other.multicolors

    def __lt__(self, other):
        """ Implementation of ``<`` operation for :class:`Multicolor`

        One :class:`Multicolor` instance is said to be "less than" the other :class:`Multicolor` instance, if it contains less or equal number of colors colors,
        as the other :class:`Multicolor` object does, and multiplicity of all of them is less or equal than in the other multicolor,
        and at least one color has multiplicity less, than in the other multicolor.
        :class:`Multicolor` instance is never less, than non-:class:`Multicolor` object.

        :param other: an object to compare to
        :type other: any python object
        :return: a flag if current :class:`Multicolor` object is less than supplied object
        :rtype: ``Boolean``
        """
        if not isinstance(other, Multicolor):
            return False
        self_keys = self.colors
        other_keys = other.colors
        return all(self.multicolors[key] <= other.multicolors[key] for key in self_keys) and \
               self_keys <= other_keys and \
               any(self.multicolors[key] < other.multicolors[key] for key in self_keys)

    def __le__(self, other):
        """ Implementation of "<=" operation for :class:`Multicolor`

        One :class:`Multicolor` instance is said to be "less or equal than" the other :class:`Multicolor` instance, if it contains less or equal number colors,
        as the other :class:`Multicolor` object does, and multiplicity of all of them is less or equal than in the other multicolor.
        :class:`Multicolor` instance is never less or equal, than non-:class:`Multicolor` object.

        :param other: an object to compare to
        :type other: any python object
        :return: a flag if current :class:`Multicolor` object is less or equal than supplied object
        :rtype: ``Boolean``
        """
        if not isinstance(other, Multicolor):
            return False
        self_keys = self.colors
        other_keys = other.colors
        return all(self.multicolors[key] <= other.multicolors[key] for key in self_keys) and self_keys <= other_keys

    def __gt__(self, other):
        """ Implementation of ``>`` operation for :class:`Multicolor`

        One :class:`Multicolor` instance is said to be "greater than" the other :class:`Multicolor` instance, if it contains greater os equal number of colors,
        as the other :class:`Multicolor` object does, and multiplicity of all of them is greater or equal than in the other multicolor,
        and at least one color has multiplicity greater, than in the other multicolor.
        :class:`Multicolor` instance is never less, than non-:class:`Multicolor` object.

        :param other: an object to compare to
        :type other: any python object
        :return: a flag if current :class:`Multicolor` object is less than supplied object
        :rtype: ``Boolean``
        """
        if not isinstance(other, Multicolor):
            return False
        self_keys = self.colors
        other_keys = other.colors
        return any(self.multicolors[key] > other.multicolors[key] for key in self_keys) and \
               self_keys >= other_keys and \
               all(self.multicolors[key] >= other.multicolors[key] for key in self_keys)

    def __ge__(self, other):
        """ Implementation of ">=" operation for :class:`Multicolor`

        One :class:`Multicolor` instance is said to be "greater than" the other :class:`Multicolor` instance, if it contains greater or equal number of colors,
        as the other :class:`Multicolor` object does, and multiplicity of all of them is greater or equal than in the other multicolor.
        :class:`Multicolor` instance is never less, than non-:class:`Multicolor` object.

        :param other: an object to compare to
        :type other: any python object
        :return: a flag if current :class:`Multicolor` object is greater or equal than supplied object
        :rtype: ``Boolean``
        """
        if not isinstance(other, Multicolor):
            return False
        self_keys = self.colors
        other_keys = other.colors
        return all(self.multicolors[key] >= other.multicolors[key] for key in self_keys) and self_keys >= other_keys

    @property
    def colors(self):
        """ Implements an "attribute" like object to access information about colors only, hiding information about their multiplicity.

        Creates a fresh set object every time is accessed.

        :return: all colors that current :class:`Multicolor` object contains information about.
        :rtype: ``set``
        """
        return set(self.multicolors.keys())

    @property
    def hashable_representation(self):
        """ For a sake of speed check for multicolor presence, each multicolor has a deterministic hashable representation """
        return tuple(sorted(self.multicolors.elements()))

    def __mul__(self, other):
        """ Multicolor can be multiplied by a number and it multiplies multiplicity of each present color respectively

        :param other: an integer multiplier
        :return: a new multicolor object resulted from multiplying each colors multiplicity by the multiplier
        """
        if not isinstance(other, int) or other < 0:
            raise TypeError("Multicolor can be multiplied only by integer values")
        if other == 0:
            return Multicolor()
        result = deepcopy(self)
        for value in result.multicolors:
            result.multicolors[value] *= other
        return result

    def intersect(self, other):
        """ Computes the multiset intersection, between the current Multicolor and the supplied Multicolor

        :param other: another Multicolor object to compute a multiset intersection with
        :return:
        :raise TypeError: an intersection can be computed only between two Multicolor objects
        """
        if not isinstance(other, Multicolor):
            raise TypeError("Multicolor can be intersected only with another Multicolor object")
        intersection_colors_core = self.colors.intersection(other.colors)
        colors_count = {color: min(self.multicolors[color], other.multicolors[color]) for color in intersection_colors_core}
        return Multicolor(*(color for color in colors_count for _ in range(colors_count[color])))
