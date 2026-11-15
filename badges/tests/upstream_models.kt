// Test-only model adapters. Production matcher code is downloaded by pinned
// commit, hash-verified and extracted verbatim into an ignored build directory.
// These adapters avoid Android/Compose/serialization dependencies. They do not
// implement matching, candidate collection, grouping, regex or deduplication.
data class StreamBadge(val name:String="",val imageURL:String="",val tagColor:String="",val tagStyle:String="",val textColor:String="",val borderColor:String="")
data class StreamBadgeFilter(val id:String="",val groupId:String="",val name:String="",val pattern:String="",val imageURL:String="",val isEnabled:Boolean=true,val tagColor:String="",val tagStyle:String="",val textColor:String="",val borderColor:String="")
data class StreamBadgeImport(val filters:List<StreamBadgeFilter>,val isActive:Boolean=true)
data class StreamBadgeRules(val imports:List<StreamBadgeImport>) {
    val hasImport:Boolean get()=imports.isNotEmpty()
    // Every fixture uses one already-normalized, active import.
    fun normalized():StreamBadgeRules=this
}
data class Parsed(val rawTitle:String?=null,val parsedTitle:String?=null,val resolution:String?=null,val quality:String?=null,val codec:String?=null,val edition:String?=null,val audio:List<String>?=null,val channels:List<String>?=null,val hdr:List<String>?=null,val group:String?=null)
data class Raw(val filename:String?=null,val torrentName:String?=null,val parsed:Parsed?=null)
data class ResolvedStream(val raw:Raw?=null)
data class Resolve(val stream:ResolvedStream?=null,val filename:String?=null,val torrentName:String?=null)
data class Hints(val filename:String?=null)
data class CacheStatus(val cachedName:String?=null)
data class Stream(val clientResolve:Resolve?=null,val behaviorHints:Hints=Hints(),val debridCacheStatus:CacheStatus?=null,val name:String?=null,val title:String?=null,val description:String?=null,val addonName:String?=null,val sourceName:String?=null)
typealias StreamItem=Stream
