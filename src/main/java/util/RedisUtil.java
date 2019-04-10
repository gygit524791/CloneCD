package util;

import ccd.PropsLoader;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.util.Iterator;
import java.util.Set;

public class RedisUtil {
    private static JedisPool jedisPool = null;
    private static int rid;

    /**
     *  init
     */
    static {
        String ADDR = PropsLoader.getProperty("redis.addr");
        int PORT = Integer.valueOf(PropsLoader.getProperty("redis.port"));
        int MAX_ACTIVE = Integer.valueOf(PropsLoader.getProperty("redis.max_active"));
        int MAX_IDLE = Integer.valueOf(PropsLoader.getProperty("redis.max_idle"));
        int MAX_WAIT = Integer.valueOf(PropsLoader.getProperty("redis.max_wait"));
        rid = Integer.valueOf(PropsLoader.getProperty("redis.rid"));
        boolean TEST_ON_BORROW = Boolean.valueOf(PropsLoader.getProperty("redis.test_on_borrow"));
        try {
            JedisPoolConfig config = new JedisPoolConfig();
            config.setMaxTotal(MAX_ACTIVE);
            config.setMaxIdle(MAX_IDLE);
            config.setMaxWaitMillis(MAX_WAIT);
            config.setTestOnBorrow(TEST_ON_BORROW);
            jedisPool = new JedisPool(config, ADDR, PORT);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public synchronized static Jedis getJedis() {
        try {
            if (jedisPool != null) {
                Jedis resource = jedisPool.getResource();
                resource.select(rid);
                return resource;
            } else {
                return null;
            }
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static void returnResource(final Jedis jedis) {
        if (jedis != null) {
            jedisPool.returnResourceObject(jedis);
        }
    }

    public static void init(){
        openDB();
        clearDB();
        flushAll();
    }

    public static void openDB(){
        final Runtime runtime = Runtime.getRuntime();
        try {
            runtime.exec(PropsLoader.getProperty("redis.path"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void clearDB(){
        getJedis().flushDB();
    }

    public static void flushAll(){
        getJedis().flushAll();
    }

    public static void checkSet(){
        Set<String> keys = getJedis().keys("*");
        System.out.println(keys.size());
        Iterator<String> it = keys.iterator();
        while (it.hasNext()){
            String key = it.next();
            System.out.println(key);
        }
    }
}