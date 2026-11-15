import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.Pattern;

/** Java Pattern + find(), ordered URL dedupe, and candidates as used by Nuvio TV.
 * No invented first-match-per-group behavior. Input is base64 TSV, not executable code.
 */
public class BadgeRegexHarness {
    record Filter(String id, String url, Pattern pattern) {}
    static String decode(String value) {
        return new String(Base64.getDecoder().decode(value), StandardCharsets.UTF_8);
    }
    public static void main(String[] args) throws Exception {
        var filters = new ArrayList<Filter>();
        for (String line : Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8)) {
            String[] p = line.split("\t", -1);
            filters.add(new Filter(p[0], decode(p[1]), Pattern.compile(decode(p[2]))));
        }
        for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
            String[] fields = line.split("\t", -1);
            var candidates = new ArrayList<String>();
            for (int i = 1; i < fields.length; i++) {
                String s = decode(fields[i]).replaceAll("\\s+", " ").trim();
                if (!s.isBlank() && !candidates.contains(s)) candidates.add(s);
            }
            if (candidates.size() > 1) candidates.add(String.join(" ", candidates));
            var hits = new ArrayList<String>();
            var seen = new HashSet<String>();
            for (Filter f : filters) {
                if (candidates.stream().anyMatch(s -> f.pattern().matcher(s).find()) && seen.add(f.url())) hits.add(f.id());
            }
            System.out.println(fields[0] + "\t" + String.join(",", hits));
        }
    }
}
